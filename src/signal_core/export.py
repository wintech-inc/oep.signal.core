"""CRM export (M4): the in-market companies of a discovery run as a CSV for the CRM's SIGNAL import page.

    in-market companies from data/discovery/<market>.json
    stage 2 for any whose role is from an older stage-2 prompt     (cached)
    one map lookup per company for address and phone              (cached)
    geography gate on the found address
    merge duplicates (same phone number or same homepage)
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

from signal_core.companies import Company, is_social, load_companies
from signal_core.discover import (
    CONTACT_FIELDS, EVAL_DIR, STATE_CODES, US_STATES, Discovery, display_name, lead_url, norm_name, parse_town,
    same_place, state_of, write_leads,
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


def homepage(url: str, listing_website: str | None = None) -> str:
    """The company's homepage, https:// plus the host with no path. A social page or a deep page gives way to
    the website on the company's map listing; without one, it is kept as it is, since it at least leads to
    the company and its host may be someone else's site."""
    if not is_social(url) and not is_deep(url):
        return f"https://{urlsplit(url).hostname}"
    site = lead_url(listing_website)
    if site and not is_social(site):
        return f"https://{urlsplit(site).hostname}"
    return lead_url(url) or url


def is_supplier(name: str, supplier: str) -> bool:
    """True for the brief's supplier itself (discovery can find our own pages)."""
    ours = norm_name(supplier.split("(")[0])
    return bool(ours) and ours in norm_name(name)


def phone_digits(phone: str | None) -> str:
    digits = re.sub(r"\D", "", phone or "")
    return digits[-10:] if len(digits) >= 10 else ""


def contact(places: list[dict], company_id: str, names: list[str], known_state: str | None, query: str) -> dict:
    """Address, phone, and website from the first map listing that is the company's (discovery's `locate` rule).
    A listing in another state than the one the company is known to be in is not its listing."""
    for p in places:
        if not same_place(p, company_id, names):
            continue
        address = split_address(p["address"])
        if known_state and address["state"] and address["state"] != known_state:
            continue
        return {**address, "phone": p.get("phone") or "", "website": p.get("website") or "",
                "maps_url": f"https://www.google.com/maps?cid={p['cid']}" if p.get("cid") else "",
                "town": parse_town(p["address"]), "query": query}
    return {**dict.fromkeys(CONTACT_FIELDS, ""), "town": None, "query": query}


def merge_duplicates(rows: list[dict]) -> tuple[list[dict], list[tuple[dict, dict]]]:
    """Rows with the same homepage, or the same phone number and names that contain one another, or the same
    name and no conflicting state or phone, are one company (typically its Facebook page and its website).
    A phone number alone is not enough (dealers and sister companies share numbers), and nor is a name alone
    (same-named businesses in other states, or one company's separate locations, each have their own number).
    The own-site row is kept, with blank contact fields filled from the others.
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

    def fits(a: str, b: str) -> bool:
        return not a or not b or a == b

    for i, r in enumerate(rows):
        if name := norm_name(r["Company"]):
            for j in by_name.setdefault(name, []):
                if fits(r["State"], rows[j]["State"]) and fits(phone_digits(r["Phone"]), phone_digits(rows[j]["Phone"])):
                    parent[find(i)] = find(j)
            by_name[name].append(i)
        home = r["Homepage"].split("://")[-1].removeprefix("www.").rstrip("/").lower()
        parent[find(i)] = find(by_home.setdefault(home, i))
        if phone := phone_digits(r["Phone"]):
            a = norm_name(r["Company"])
            for j in by_phone.setdefault(phone, []):
                b = norm_name(rows[j]["Company"])
                if a and b and (a in b or b in a):
                    parent[find(i)] = find(j)
            by_phone[phone].append(i)
    groups: dict[int, list[int]] = {}
    for i in range(len(rows)):
        groups.setdefault(find(i), []).append(i)
    kept, merged = [], []
    for members in groups.values():
        best = min(members, key=lambda i: (is_social(rows[i]["_url"]), is_deep(rows[i]["_url"]), i))
        row = rows[best]
        for i in members:
            if i == best:
                continue
            for column in ("Street address", "City", "State", "ZIP", "Phone", "CRM Status"):
                row[column] = row[column] or rows[i][column]
            merged.append((row, rows[i]))
        kept.append((best, row))
    return [row for _, row in sorted(kept, key=lambda x: x[0])], merged


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
    ct = c.get("contact") or {}
    url = role_url(c)
    return {
        "Company": display_name(c), "Homepage": homepage(c["url"], ct.get("website")),
        "Target": market.crm_target or "", "Division": market.crm_market or "", "Role": c["role"],
        "Street address": ct.get("street", ""), "City": ct.get("city", ""), "State": ct.get("state", ""),
        "ZIP": ct.get("zip", ""), "Phone": ct.get("phone", ""),
        "Comments": (c.get("comment") or "").strip() + (f" Source: {url}" if url else ""),
        "Lead Source": LEAD_SOURCE, "CRM Status": crm_status(list(crm)),
        "_url": c["url"], "_maps": ct.get("maps_url", ""),
    }


# The export


async def lookup_contacts(d: Discovery) -> None:
    """One map lookup per in-market company without one: '<name> <town, state>' when the town is known."""
    todo = [c for c in d.in_market() if "contact" not in c and c.get("role") in ROLES]
    done = 0

    async def one(c):
        nonlocal done
        town = parse_town(c.get("location"))
        name = display_name(c)
        query = f"{name} {town}" if town else name
        async with d.slots:
            if d.over_budget():
                return
            try:
                places = (await d.fetcher.places(query))["results"]
            except httpx.HTTPError:
                return
        c["contact"] = contact(places, c["company_id"], list(dict.fromkeys([name, c["name"]])), state_of(town), query)
        if not c.get("location") and c["contact"]["town"]:
            c["location"] = c["contact"]["town"]
        done += 1
        d.progress(f"map lookups {done}/{len(todo)}")

    await asyncio.gather(*(one(c) for c in todo))


async def export(market: Market, max_cost: float = MAX_COST) -> dict:
    """Bring roles and contact data up to date in the discovery state, then write the CRM file and sheets."""
    async with Discovery(market, max_cost=max_cost) as d:
        if not d.candidates:
            raise SystemExit(f"No discovery run for {market.id}. Run: signal discover --market {market.id}")
        before = len(d.in_market())
        await d.refresh_roles()
        await lookup_contacts(d)
        for c in d.in_market():
            d.gate(c)
        d.finish("export")
        cost = d.cost()
        print(file=sys.stderr)
    ins = d.in_market()
    order = {r: i for i, r in enumerate(ROLES)}
    ready = sorted((c for c in ins if c.get("role") in ROLES and c.get("role_version") == d.role_version),
                   key=lambda c: (order[c["role"]], state_of(c.get("location")) or "~", display_name(c).lower()))
    not_ready = len(ins) - len(ready)
    ours = {c["company_id"] for c in ready if is_supplier(display_name(c), market.supplier)}
    ready = [c for c in ready if c["company_id"] not in ours]
    known = {k.id: k for k in load_companies()}
    by_name: dict[str, list[Company]] = {}
    for k in known.values():
        for n in dict.fromkeys(norm_name(x) for x in [k.name, *k.aliases]):
            by_name.setdefault(n, []).append(k)
    rows, merged = merge_duplicates([crm_row(market, c, crm_matches(c, known, by_name)) for c in ready])
    paths = {"crm": EXPORTS_DIR / f"crm_{market.id}.csv", "leads": write_leads(market.id, d.state),
             "report": EVAL_DIR / f"export_{market.id}.md", "contacts": EVAL_DIR / f"review_contacts_{market.id}.csv"}
    write_csv(paths["crm"], CRM_COLUMNS, rows)
    filled = [r for r in rows if r["Phone"] or r["City"]]
    sample = random.Random(SEED).sample(filled, min(SPOT_CHECK, len(filled)))
    write_csv(paths["contacts"], CONTACT_SHEET_COLUMNS, [{**r, "maps_url": r["_maps"]} for r in sample])
    summary = {"market": market, "rows": rows, "merged": merged, "gated": before - len(ins), "ours": len(ours),
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
        f"Blank means no map listing matched the company; nothing is guessed. Spot-check sheet: "
        f"`{paths['contacts'].relative_to(ROOT)}`.", "",
        "## Not exported", "",
        f"- Found by the map lookup to be based outside the market's geography: {s['gated']}.",
        f"- {market.supplier} itself (pages discovery found under its name): {s['ours']}.",
        f"- In the market but without a role from the current stage-2 prompt (budget stop or errors; run again): "
        f"{s['not_ready']}.", "",
        "## Duplicates merged", "",
    ]
    lines += [f"- {kept['Company']} ({kept['_url']}) kept; {dropped['Company']} ({dropped['_url']}) dropped"
              for kept, dropped in s["merged"]] or ["None."]
    lines += ["", f"This export's API and search spend: ${s['cost']:.2f}.", ""]
    return "\n".join(lines)
