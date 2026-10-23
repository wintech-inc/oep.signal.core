"""CRM export (M4): the in-market companies of a discovery run as a CSV for the CRM's SIGNAL import page.

    in-market companies from data/discovery/<market>.json
    stage 2 for any whose role is from an older stage-2 prompt     (cached)
      (it also gives the company's own website and where it is based)
    one map lookup per company for address and phone, in the town stage 2 gives   (cached)
    for a blank phone or street address: the company's own homepage and contact page
      (a social-only company: one web search), read by one small LLM call   (cached)
    geography gate on where stage 2, the map listing, or the website places the company
    merge duplicates (same homepage, same phone, same name, or a social page named after a row's domain)
    -> exports/crm_<market>.csv, eval/leads_<market>.csv, eval/export_<market>.md,
       eval/review_contacts_<market>.csv (contact spot check)
"""

import asyncio
import csv
import random
import re
import sys
from collections import Counter
from pathlib import Path
from urllib.parse import urlsplit

import httpx
from pydantic import BaseModel

from signal_core.classify import MODEL
from signal_core.companies import Company, bare_host, is_social, load_companies
from signal_core.discover import (
    CONTACT_FIELDS, EVAL_DIR, PROMPTS, STATE_CODES, US_STATES, Discovery, display_name, lead_url, merged_contact,
    norm_name, parse_town, same_place, state_of, write_leads,
)
from signal_core.markets import LEAD_ROLES, ROLES, ROOT, Market
from signal_core.role import role_url

EXPORTS_DIR = ROOT / "exports"
CRM_COLUMNS = ["Company", "Homepage", "Target", "Division", "Role", "Street address", "City", "State", "ZIP", "Phone",
               "Comments", "Lead Source", "CRM Status"]
LEAD_SOURCE = "SIGNAL"
MAX_COST = 10.0
SPOT_CHECK = 25
SEED = 13
PAGE_HEAD, PAGE_TAIL = 3000, 5000   # homepage text read for contact details: its start and its footer
CONTACT_PAGE_CHARS = 8000
US_NAMES = {"us", "usa", "u.s.", "u.s.a.", "united states", "united states of america"}
CONTACT_SHEET_COLUMNS = ["Company", "Homepage", "Street address", "City", "State", "ZIP", "Phone", "maps_url",
                         "address_right", "phone_right", "note"]


# Small pure helpers (unit tested)


def split_address(address: str | None) -> dict:
    """A US map listing's address split into street, city, state, and ZIP ('12 Main St, Cullman, AL 35055').
    Service-area listings often give only 'Cullman, AL'. What isn't there, or isn't a US state, stays blank."""
    out = dict.fromkeys(("street", "city", "state", "zip"), "")
    parts = [p.strip() for p in (address or "").split(",") if p.strip()]
    if parts and parts[-1].lower() in ("united states", "usa", "us"):
        parts.pop()
    if not parts:
        return out
    m = re.fullmatch(r"([A-Za-z][A-Za-z .]*?)\s*(\d{5}(?:-\d{4})?)?", parts[-1])
    region = m.group(1).strip() if m else ""
    state = STATE_CODES.get(region.lower()) or (region.upper() if region.upper() in US_STATES else None)
    if not state:
        return out
    out.update(state=state, zip=m.group(2) or "")
    if len(parts) >= 2:
        out.update(city=parts[-2], street=", ".join(parts[:-2]))
    return out


def is_deep(url: str) -> bool:
    """A page below a site's root, which discovery may have found on another site (a news article, a dealer's
    product page) rather than on the company's own."""
    return not is_social(url) and bool(urlsplit(url).path.strip("/"))


def names_site(name: str, url: str) -> bool:
    """True when a site's domain carries the company's name, or a word of it ('Big Dutchman' and
    bigdutchmanusa.com; not 'Lazy Man Outdoors' and printkindred.com)."""
    label = norm_name(bare_host(url).rsplit(".", 1)[0])
    whole = norm_name(name)
    words = [w for w in re.findall(r"[a-z0-9]+", name.lower()) if len(w) >= 4]
    return bool(label and whole) and (whole in label or (len(label) >= 4 and label in whole) or any(w in label for w in words))


def homepage(url: str, own_website: str = "", listing_website: str | None = None, name: str = "") -> str:
    """The company's homepage, https:// plus the host with no path: the website stage 2 found in the evidence;
    else the page discovery found if it is on a site of the company's own (not deep, or named after it);
    else the map listing's website if named after the company or the found page's site; else the social or
    found page as it is."""
    if own_website:
        return own_website
    if not is_social(url) and (not is_deep(url) or names_site(name, url)):
        return f"https://{urlsplit(url).hostname}"
    site = lead_url(listing_website)
    if site and not is_social(site) and (names_site(name, site) or bare_host(site) == bare_host(url)):
        return f"https://{urlsplit(site).hostname}"
    return lead_url(url) or url


def is_supplier(name: str, supplier: str) -> bool:
    """True for the brief's supplier itself (discovery can find our own pages)."""
    ours = norm_name(supplier.split("(")[0])
    return bool(ours) and ours in norm_name(name)


def phone_digits(phone: str | None) -> str:
    digits = re.sub(r"\D", "", phone or "")
    return digits[-10:] if len(digits) >= 10 else ""


def contact(places: list[dict], company_id: str, names: list[str], known_state: str | None, query: str,
            own_site: str = "") -> dict:
    """Address, phone, and website from the first map listing that is the company's (discovery's `locate` rule).
    A listing in another state than the one the company is known to be in, or with a website other than the
    company's own, is not its listing."""
    for p in places:
        if not same_place(p, company_id, names):
            continue
        address = split_address(p["address"])
        if known_state and address["state"] and address["state"] != known_state:
            continue
        site = lead_url(p.get("website"))
        if own_site and site and not is_social(site) and bare_host(site) != bare_host(own_site):
            continue
        phone = p.get("phone") or ""
        return {**address, "phone": phone if len(re.sub(r"\D", "", phone)) >= 10 else "", "website": p.get("website") or "",
                "maps_url": f"https://www.google.com/maps?cid={p['cid']}" if p.get("cid") else "",
                "address": p["address"], "town": parse_town(p["address"]), "query": query}
    return {**dict.fromkeys(CONTACT_FIELDS, ""), "address": "", "town": None, "query": query}


def contact_links(text: str, site_url: str) -> list[str]:
    """Links to the same site's contact page in a page's text with inline links ('Contact Us [https://...]')."""
    host = bare_host(site_url)
    links = re.findall(r"\[(https?://[^\]\s]+)\]", text)
    return list(dict.fromkeys(u for u in links if bare_host(u) == host and "contact" in u.lower()))


def excerpt(text: str) -> str:
    """A homepage's start and its footer, where contact details usually are."""
    return text if len(text) <= PAGE_HEAD + PAGE_TAIL else text[:PAGE_HEAD] + " ... " + text[-PAGE_TAIL:]


def clean_site_contact(answer: dict, source: str) -> dict:
    """Keep a phone with at least ten digits and a US address whose state is a real state code; a foreign
    country is kept so the geography gate can see it."""
    out = {"source": source, "country": (answer.get("country") or "").strip()}
    phone = (answer.get("phone") or "").strip()
    out["phone"] = phone if len(re.sub(r"\D", "", phone)) >= 10 else ""
    state = (answer.get("state") or "").strip()
    state = STATE_CODES.get(state.lower()) or (state.upper() if state.upper() in US_STATES else "")
    if state and (not out["country"] or out["country"].lower() in US_NAMES):
        out.update(street=(answer.get("street") or "").strip(), city=(answer.get("city") or "").strip(), state=state,
                   zip=(answer.get("zip") or "").strip())
    return out


def town_of(c: dict) -> str | None:
    """'Town, ST' where the company is based: stage 2's reading of the evidence, else discovery's location."""
    return parse_town(c.get("based_in")) or parse_town(c.get("location"))


def us_phone(phone: str | None) -> str:
    """A US or North American number in one format, '270-748-2541' (the CRM reads '(270) ...' as a country
    code); "" for anything else (another country's
    code, or digits that can't be a North American number, such as '1300-655-735 (AUS)')."""
    if not phone or is_foreign_phone(phone):
        return ""
    digits = re.sub(r"\D", "", phone.split("x")[0].split("ext")[0])
    digits = digits[1:] if len(digits) == 11 and digits[0] == "1" else digits
    if not re.fullmatch(r"[2-9]\d{2}[2-9]\d{6}", digits):
        return ""
    return f"{digits[:3]}-{digits[3:6]}-{digits[6:]}"


def is_foreign_phone(phone: str | None) -> bool:
    """A number written with a country code other than +1."""
    return bool(phone) and phone.startswith("+") and not phone.startswith("+1")


def abroad(c: dict, home: set[str]) -> str | None:
    """Why stage 2, the map listing, or the company's own pages place it outside the market's geography (a
    country other than the US, a state or province outside `home`, a phone number with another country's code).
    A listing address with no state at all (often just a street) says nothing. Stage 2 placing the company in
    a US state inside `home` settles it: a foreign number then belongs to a parent company or a same-named
    business, and is left out of the export instead. None if nothing does."""
    ct, site = c.get("contact") or {}, c.get("site_contact") or {}
    if c.get("based_country") and c["based_country"].lower() not in US_NAMES:
        return f"stage 2 places it in {', '.join(x for x in (c.get('based_in'), c['based_country']) if x)}"
    if (state := state_of(town_of(c))) and home and state not in home:
        return f"based in {town_of(c)}"
    if state and c.get("based_country"):
        return None
    if (state := state_of(ct.get("address"))) and home and state not in home:   # a province or a state outside it
        return f"map listing address {ct['address']}"
    for source, phone in (("map listing", ct.get("phone")), (site.get("source"), site.get("phone"))):
        if is_foreign_phone(phone):
            return f"{source} phone {phone}"
    if site.get("country") and site["country"].lower() not in US_NAMES:
        return f"{site['source']} address in {site['country']}"
    return None


LEGAL_SUFFIXES = {"inc", "incorporated", "llc", "co", "corp", "corporation", "company", "ltd"}


def base_name(name: str) -> str:
    """A company name without its legal suffix, letters and digits only ('Formex Manufacturing, Inc.' ->
    'formexmanufacturing')."""
    words = re.findall(r"[a-z0-9]+", name.lower())
    while len(words) > 1 and words[-1] in LEGAL_SUFFIXES:
        words.pop()
    return "".join(words)


def first_word(name: str) -> str:
    return next(iter(re.findall(r"[a-z0-9]+", name.lower())), "")


def merge_duplicates(rows: list[dict]) -> tuple[list[dict], list[tuple[dict, dict]]]:
    """Rows with the same homepage, or the same phone number and names that contain one another or start with
    the same word, or the same name (legal suffixes aside) and the same state or no conflicting state or phone,
    are one company (typically its Facebook page and its website, or two of its sites). A phone number alone
    is not enough (dealers and sister companies share numbers), and nor is a name alone (same-named businesses
    in other states each have their own number). The row on the company's own, name-bearing site is kept,
    with blank contact fields filled from the others.
    Returns the kept rows, in order, and (kept, dropped) row pairs."""
    parent = list(range(len(rows)))

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    by_home: dict[str, int] = {}
    by_phone: dict[str, list[int]] = {}
    by_name: dict[str, list[int]] = {}
    by_handle: dict[str, list[int]] = {}
    by_label: dict[str, list[int]] = {}

    def fits(a: str, b: str) -> bool:
        return not a or not b or a == b

    for i, r in enumerate(rows):
        if handle := social_handle(r["Homepage"]):
            for j in by_label.get(handle, []):
                parent[find(i)] = find(j)
            by_handle.setdefault(handle, []).append(i)
        elif label := site_label(r["Homepage"]):
            for j in by_handle.get(label, []):
                parent[find(i)] = find(j)
            by_label.setdefault(label, []).append(i)
        if name := base_name(r["Company"]):
            for j in by_name.setdefault(name, []):
                same_state = r["State"] and r["State"] == rows[j]["State"]
                if same_state or (fits(r["State"], rows[j]["State"])
                                  and fits(phone_digits(r["Phone"]), phone_digits(rows[j]["Phone"]))):
                    parent[find(i)] = find(j)
            by_name[name].append(i)
        home = r["Homepage"].split("://")[-1].removeprefix("www.").rstrip("/").lower()
        parent[find(i)] = find(by_home.setdefault(home, i))
        if phone := phone_digits(r["Phone"]):
            a = norm_name(r["Company"])
            for j in by_phone.setdefault(phone, []):
                b = norm_name(rows[j]["Company"])
                if a and b and (a in b or b in a or first_word(r["Company"]) == first_word(rows[j]["Company"])):
                    parent[find(i)] = find(j)
            by_phone[phone].append(i)
    groups: dict[int, list[int]] = {}
    for i in range(len(rows)):
        groups.setdefault(find(i), []).append(i)
    kept, merged = [], []
    for members in groups.values():
        best = min(members, key=lambda i: (is_social(rows[i]["_url"]), not names_site(rows[i]["Company"], rows[i]["Homepage"]),
                                           is_deep(rows[i]["_url"]), i))
        row = rows[best]
        for i in members:
            if i == best:
                continue
            for column in ("Street address", "City", "State", "ZIP", "Phone", "CRM Status"):
                row[column] = row[column] or rows[i][column]
            merged.append((row, rows[i]))
        kept.append((best, row))
    return [row for _, row in sorted(kept, key=lambda x: x[0])], merged


def social_handle(url: str) -> str:
    """A social page's handle, letters and digits only ('instagram.com/deerview_windows' -> 'deerviewwindows')."""
    return norm_name(urlsplit(url).path.strip("/").split("/")[0]) if is_social(url) else ""


def site_label(url: str) -> str:
    """A website's name without its ending ('https://www.padeerblinds.com' -> 'padeerblinds')."""
    return "" if is_social(url) else norm_name(bare_host(url).rsplit(".", 1)[0])


def crm_status(companies: list[Company]) -> str:
    """The company's role in the CRM list it came from ('Lead', 'Customer', ...), blank when it isn't on it.
    The few companies with several CRM rows get each distinct role, alphabetically."""
    return "; ".join(sorted({t.role for c in companies for t in c.crm}))


def crm_matches(c: dict, known: dict[str, Company], by_name: dict[str, list[Company]]) -> list[Company]:
    """The CRM list's entry for a company: the same website or page, else exactly the same name (the CRM may
    hold its website while discovery found its Facebook page, or the other way round)."""
    if c["company_id"] in known:
        return [known[c["company_id"]]]
    names = dict.fromkeys(norm_name(n) for n in (display_name(c), c["name"]))
    return list({k.id: k for n in names if n for k in by_name.get(n, [])}.values())


def crm_row(market: Market, c: dict, crm: list[Company] = ()) -> dict:
    ct = merged_contact(c)
    ct["phone"] = us_phone(ct["phone"])
    if ct["city"].isupper() or ct["city"].islower():   # 'BENTON', 'cincinnati'
        ct["city"] = ct["city"].title()
    url = role_url(c)
    return {
        "Company": display_name(c),
        "Homepage": homepage(c["url"], c.get("own_website") or "", ct.get("website"), display_name(c)),
        "Target": market.crm_target or "", "Division": market.crm_market or "", "Role": c["role"],
        "Street address": ct.get("street", ""), "City": ct.get("city", ""), "State": ct.get("state", ""),
        "ZIP": ct.get("zip", ""), "Phone": ct.get("phone", ""),
        "Comments": (c.get("comment") or "").strip() + (f" Source: {url}" if url else ""),
        "Lead Source": LEAD_SOURCE, "CRM Status": crm_status(list(crm)),
        "_url": c["url"], "_maps": ct.get("maps_url", ""), "_from_site": ct["from_site"],
    }


# The export


def lookup_query(c: dict) -> str:
    town = town_of(c)
    return f"{display_name(c)} {town}" if town else display_name(c)


async def lookup_contacts(d: Discovery) -> None:
    """One map lookup per in-market company, '<name> <town, state>' when the town is known; again when stage 2
    names another town."""
    todo = [c for c in d.in_market() if c.get("role") in ROLES and (
        "address" not in (c.get("contact") or {}) or c["contact"].get("query") != lookup_query(c))]
    done = 0

    async def one(c):
        nonlocal done
        town, name, query = town_of(c), display_name(c), lookup_query(c)
        async with d.slots:
            if d.over_budget():
                return
            try:
                places = (await d.fetcher.places(query))["results"]
            except httpx.HTTPError:
                return
        c["contact"] = contact(places, c["company_id"], list(dict.fromkeys([name, c["name"]])), state_of(town), query,
                               c.get("own_website") or "")
        if not c.get("location") and c["contact"]["town"]:
            c["location"] = c["contact"]["town"]
        done += 1
        d.progress(f"map lookups {done}/{len(todo)}")

    await asyncio.gather(*(one(c) for c in todo))


class SiteContact(BaseModel):
    phone: str | None
    street: str | None
    city: str | None
    state: str | None
    zip: str | None
    country: str | None


async def read_site_contacts(d: Discovery) -> None:
    """For in-market companies whose phone or street address the map listing left blank: their own homepage and
    contact page, or for a company without a site of its own one web search, read by one small LLM call."""
    todo = [c for c in d.in_market() if c.get("role") in ROLES and "site_contact" not in c
            and not all(merged_contact(c)[k] for k in ("phone", "street"))]
    prompt = (PROMPTS / "read_contact.md").read_text()
    done = 0

    async def one(c):
        nonlocal done
        async with d.slots:
            if d.over_budget():
                return
            name = display_name(c)
            site = homepage(c["url"], c.get("own_website") or "", (c.get("contact") or {}).get("website"), name)
            try:
                if is_social(site) or is_deep(site):   # no site we can be sure is the company's own
                    source, town = "web search", town_of(c) or ""
                    query = f'"{name}" {town} phone'.replace("  ", " ")
                    results = (await d.fetcher.web_page(query))["results"]
                    text = "\n".join(f"{r['title']} ({r['link']})\n{r['snippet']}" for r in results)
                    user = f"Company: {name}\nSocial page: {c['url']}\n\nSearch results for: {query}\n\n{text}"
                else:
                    source = "website"
                    home = await d.fetcher.list_page(site + "/")
                    parts = [f"## Homepage ({home['final_url'] or site})", excerpt(home["text"])]
                    for link in contact_links(home["text"], home["final_url"] or site)[:1]:
                        page = await d.fetcher.list_page(link)
                        parts += [f"## Contact page ({link})", page["text"][:CONTACT_PAGE_CHARS]]
                    text = "\n\n".join(parts)
                    user = f"Company: {name}\nWebsite: {site}\n\n{text}"
            except httpx.HTTPError:
                return
            if not text.strip():
                c["site_contact"] = {"source": source}
            else:
                answer = await d.ask(MODEL, prompt, user, SiteContact, max_tokens=1000)
                if answer is None:
                    return
                c["site_contact"] = clean_site_contact(answer.model_dump(), source)
        done += 1
        d.progress(f"contact pages {done}/{len(todo)}")

    await asyncio.gather(*(one(c) for c in todo))


async def export(market: Market, max_cost: float = MAX_COST) -> dict:
    """Bring roles and contact data up to date in the discovery state, then write the CRM file and sheets."""
    async with Discovery(market, max_cost=max_cost) as d:
        if not d.candidates:
            raise SystemExit(f"No discovery run for {market.id}. Run: signal discover --market {market.id}")
        before = len(d.in_market())
        await d.refresh_roles()
        await lookup_contacts(d)
        await read_site_contacts(d)
        for c in d.in_market():
            d.gate(c, abroad(c, d.home))
        d.finish("export")
        cost = d.cost()
        print(file=sys.stderr)
    ins = d.in_market()
    order = {r: i for i, r in enumerate(ROLES)}
    ready = sorted((c for c in ins if c.get("role") in ROLES and c.get("role_version") == d.role_version),
                   key=lambda c: (order[c["role"]], state_of(c.get("location")) or "~", display_name(c).lower()))
    not_ready = len(ins) - len(ready)
    ours = {c["company_id"] for c in ready if is_supplier(display_name(c), market.supplier)}
    unnamed = {c["company_id"] for c in ready if not c.get("company_name")}
    ready = [c for c in ready if c["company_id"] not in ours | unnamed]
    known = {k.id: k for k in load_companies()}
    by_name: dict[str, list[Company]] = {}
    for k in known.values():
        for n in dict.fromkeys(norm_name(x) for x in [k.name, *k.aliases]):
            by_name.setdefault(n, []).append(k)
    rows, merged = merge_duplicates([crm_row(market, c, crm_matches(c, known, by_name)) for c in ready])
    paths = {"crm": EXPORTS_DIR / f"crm_{market.id}.csv", "leads": write_leads(market.id, d.state),
             "report": EVAL_DIR / f"export_{market.id}.md", "contacts": EVAL_DIR / f"review_contacts_{market.id}.csv"}
    write_csv(paths["crm"], CRM_COLUMNS, rows)
    from_site = Counter(f.split()[0] for r in rows for f in r["_from_site"].split(", ") if f)
    filled = [r for r in rows if r["Phone"] or r["City"]]
    sample = random.Random(SEED).sample(filled, min(SPOT_CHECK, len(filled)))
    write_csv(paths["contacts"], CONTACT_SHEET_COLUMNS, [{**r, "maps_url": r["_maps"]} for r in sample])
    summary = {"market": market, "rows": rows, "merged": merged, "gated": before - len(ins), "ours": len(ours),
               "unnamed": len(unnamed), "from_site": from_site,
               "not_ready": not_ready, "cost": cost, "stopped": d.stopped_on_budget or bool(d.stop_reason)}
    paths["report"].write_text(export_report(summary, paths))
    return {**summary, "paths": paths}


def write_csv(path: Path, columns: list[str], rows: list[dict]) -> None:
    path.parent.mkdir(exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def export_report(s: dict, paths: dict) -> str:
    market, rows = s["market"], s["rows"]
    roles = Counter(r["Role"] for r in rows)
    leads = sum(roles[r] for r in LEAD_ROLES)

    def fill(column):
        n = sum(1 for r in rows if r[column])
        return f"{n} ({n / len(rows):.0%})" if rows else "0"

    lines = [f"# CRM export: {market.name} (`{market.id}`)", ""]
    if s["stopped"]:
        lines += ["**This export stopped on its budget or on Serper errors before finishing.** Run `signal export` "
                  "again to continue; done work is kept.", ""]
    lines += [
        f"**{len(rows)} companies** in `{paths['crm'].relative_to(ROOT)}`, {leads} of them in lead roles "
        f"({', '.join(LEAD_ROLES)}).", "",
        "| Role | Companies |", "|---|---|", *[f"| {r} | {roles[r]} |" for r in ROLES], "",
        "## Contact fields filled", "",
        "| Street address | City | State | ZIP | Phone |", "|---|---|---|---|---|",
        "| " + " | ".join(fill(c) for c in ("Street address", "City", "State", "ZIP", "Phone")) + " |", "",
        f"Filled from the company's own website or a web search where the map listing had none: "
        f"{s['from_site']['phone']} phone numbers, {s['from_site']['address']} addresses. Blank means neither "
        f"showed it; nothing is guessed. Spot-check sheet: `{paths['contacts'].relative_to(ROOT)}`.", "",
        "## Not exported", "",
        f"- Placed outside the market's geography by stage 2, the map listing, or the company's own pages: "
        f"{s['gated']}.",
        f"- {market.supplier} itself (pages discovery found under its name): {s['ours']}.",
        f"- Pages stage 2 could not tie to a named company (a post or article title): {s['unnamed']}.",
        f"- In the market but without a role from the current stage-2 prompt (budget stop or errors; run again): "
        f"{s['not_ready']}.", "",
        "## Duplicates merged", "",
    ]
    lines += [f"- {kept['Company']} ({kept['_url']}) kept; {dropped['Company']} ({dropped['_url']}) dropped"
              for kept, dropped in s["merged"]] or ["None."]
    lines += ["", f"This export's API and search spend: ${s['cost']:.2f}.", ""]
    return "\n".join(lines)
