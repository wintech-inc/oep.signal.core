"""Company discovery (M3): find the companies in a market from every source, classify each new one with
both stages (M1, then M2, unchanged), and keep going while new rounds still find new in-market companies.

A lead is a company name with an optional URL and location, plus where it was found. A candidate is a
lead with a website, keyed by company_key(url) as in M1. The market list (every candidate, its verdicts,
and the paging and town state) lives in data/discovery/<market>.json, so a later run continues where
the last one stopped.
"""

import asyncio
import csv
import hashlib
import json
import random
import re
import sys
import time
from collections import Counter
from dataclasses import dataclass
from functools import cache
from pathlib import Path
from urllib.parse import urlsplit

import anthropic
import httpx
from pydantic import BaseModel

from signal_core.classify import EFFORT, MODEL, PRICE_IN, PRICE_OUT, PRICE_SEARCH, _bullets, system_prompt
from signal_core.companies import Company, bare_host, clean_url, company_key, is_social, load_companies
from signal_core.evidence import LIST_CHUNK_CHARS, LIST_CHUNKS, cache_get, cache_put, root_url
from signal_core.markets import MARKETS_DIR, ROOT, Market, load_market
from signal_core.role import ROLE_FIELDS, RoleClassifier, role_prompt

PROMPTS = ROOT / "prompts"
DISCOVERY_DIR = ROOT / "data" / "discovery"
EVAL_DIR = ROOT / "eval"
SOURCES = ("seed", "model", "web", "maps", "lists", "nearby", "snowball")
SONNET = "claude-sonnet-5-5"
SONNET_EFFORT = "medium"
# USD per million tokens (Sonnet 5.5). Haiku and Serper prices come from classify.py.
PRICE_SONNET_IN, PRICE_SONNET_OUT = 2.00, 10.00
MAX_PAGE = 10           # deepest result page fetched for one query
STOP_SHARE = 0.02       # stop when a round adds less than this share of new in-market companies
ROUNDS = 10
MAX_COST = 30.0
SNOWBALL_PAGES = 3      # list pages from one site search per in-market company
MORE_PAGES = 5          # more pages of the same list, read one level deep
PROBE_QUERIES = 12
PROBE_PAGES = 3
VERDICT_FIELDS = ["verdict", "rule", "reason", "evidence_url", *ROLE_FIELDS]
# Paths on social sites that are not a company's page.
SOCIAL_NON_PAGES = {"groups", "events", "watch", "marketplace", "share", "sharer", "sharer.php", "hashtag", "reel",
                    "reels", "p", "explore", "stories", "photo", "photo.php", "story.php", "permalink.php",
                    "profile.php", "login", "search", "tv", "posts"}
US_STATES = {
    "AL": "Alabama", "AK": "Alaska", "AZ": "Arizona", "AR": "Arkansas", "CA": "California", "CO": "Colorado",
    "CT": "Connecticut", "DE": "Delaware", "DC": "District of Columbia", "FL": "Florida", "GA": "Georgia",
    "HI": "Hawaii", "ID": "Idaho", "IL": "Illinois", "IN": "Indiana", "IA": "Iowa", "KS": "Kansas",
    "KY": "Kentucky", "LA": "Louisiana", "ME": "Maine", "MD": "Maryland", "MA": "Massachusetts", "MI": "Michigan",
    "MN": "Minnesota", "MS": "Mississippi", "MO": "Missouri", "MT": "Montana", "NE": "Nebraska", "NV": "Nevada",
    "NH": "New Hampshire", "NJ": "New Jersey", "NM": "New Mexico", "NY": "New York", "NC": "North Carolina",
    "ND": "North Dakota", "OH": "Ohio", "OK": "Oklahoma", "OR": "Oregon", "PA": "Pennsylvania",
    "RI": "Rhode Island", "SC": "South Carolina", "SD": "South Dakota", "TN": "Tennessee", "TX": "Texas",
    "UT": "Utah", "VT": "Vermont", "VA": "Virginia", "WA": "Washington", "WV": "West Virginia",
    "WI": "Wisconsin", "WY": "Wyoming",
}
STATE_CODES = {name.lower(): code for code, name in US_STATES.items()}


# The query file


class QueryFile(BaseModel):
    company_queries: list[str]
    nearby_queries: list[str]
    list_queries: list[str]
    list_terms: list[str]


def queries_path(market_id: str) -> Path:
    return MARKETS_DIR / f"{market_id}.discovery.json"


def load_queries(market_id: str) -> QueryFile:
    path = queries_path(market_id)
    if not path.exists():
        raise SystemExit(f"{path.relative_to(ROOT)} not found. Run: signal queries --market {market_id}")
    return QueryFile.model_validate_json(path.read_text())


@cache
def queries_prompt(market_id: str, existing: str) -> str:
    market = load_market(market_id)
    return (PROMPTS / "discovery_queries.md").read_text().format(
        supplier=market.supplier, end_product=market.end_product, our_products=market.our_products,
        end_terms=", ".join(market.end_product.terms), our_terms=", ".join(market.our_products.terms),
        not_included=_bullets(market.end_product.not_included), notes=_bullets(market.notes),
        examples=_bullets([f"{e.name} ({e.url}): rule {e.rule}" for e in market.examples_in]), existing=existing,
    ).strip()


@cache
def more_prompt(market_id: str) -> str:
    market = load_market(market_id)
    return (PROMPTS / "more_companies.md").read_text().format(
        supplier=market.supplier, end_product=market.end_product, our_products=market.our_products,
        not_included=_bullets(market.end_product.not_included), notes=_bullets(market.notes))


# LLM answers


class FoundCompany(BaseModel):
    name: str
    url: str | None
    location: str | None


class CompanyList(BaseModel):
    companies: list[FoundCompany]


class ListPage(BaseModel):
    companies: list[FoundCompany]
    more_pages: list[str]


class Pick(BaseModel):
    url: str | None


# Small pure helpers (unit tested)


@dataclass
class Lead:
    name: str
    url: str | None
    location: str | None
    source: str
    detail: str
    query: str | None = None  # the query whose page found it, for the paging rule


def lead_url(raw: str | None) -> str | None:
    """A usable company URL, or None. Social URLs are cut to the page itself (facebook.com/<page>)."""
    url = clean_url(raw or "")
    if url is None or not is_social(url):
        return url
    parts = [p for p in urlsplit(url).path.split("/") if p]
    if not parts or parts[0].lower() in SOCIAL_NON_PAGES:
        return None
    keep = 3 if parts[0].lower() == "people" else 1
    return f"https://{bare_host(url)}/{'/'.join(parts[:keep])}"


def norm_name(name: str) -> str:
    return re.sub(r"[^a-z0-9]", "", name.lower())


def title_name(title: str, url: str) -> str:
    """A company name from a search result title: the title segment that best matches the domain."""
    segments = [s.strip() for s in re.split(r"\s+[|\-–—•·:]\s+|\s+\(@", title) if s.strip()]
    if is_social(url):
        return segments[0] if segments else company_key(url)
    label = norm_name(bare_host(url).split(".")[0])

    def score(segment):
        words = [w for w in re.findall(r"[a-z0-9]+", segment.lower()) if len(w) > 1]
        return sum(w in label for w in words) / len(words) if words else 0

    best = max(segments, key=score, default="")
    return best if best and score(best) > 0 else bare_host(url)


def parse_town(text: str | None) -> str | None:
    """'Town, ST' from an address or location ('12 Main St, Cullman, AL 35055' -> 'Cullman, AL').
    Two-letter codes outside the US (a Canadian province) are kept, so the report can show them."""
    parts = [p.strip() for p in (text or "").split(",")]
    for town, region in zip(parts, parts[1:]):
        m = re.fullmatch(r"([A-Za-z][A-Za-z ]*?)(?:\s+[0-9][0-9-]{4,9}|\s+[A-Z][0-9][A-Z] ?[0-9][A-Z][0-9])?", region)
        if not m or not town or re.search(r"\d", town):
            continue
        name = m.group(1)
        code = STATE_CODES.get(name.lower()) or (name.upper() if name.upper() in US_STATES or re.fullmatch(r"[A-Z]{2}", name) else None)
        if code:
            return f"{town}, {code}"
    return None


def state_of(location: str | None) -> str | None:
    town = parse_town(location)
    return town.rsplit(", ", 1)[1] if town else None


def query_id(kind: str, q: str) -> str:
    return f"{kind}|{q}"


def new_query(source: str, kind: str, q: str) -> dict:
    return {"source": source, "kind": kind, "q": q, "page": 0, "round": None, "keys": [], "settled": True, "due": True}


def first_queries(queries: QueryFile, locations: list[str], sources: set[str]) -> dict[str, dict]:
    """Every web, maps, and list query of round 1: company queries nationally and per location, list queries."""
    out = {}
    for q in queries.company_queries:
        if "web" in sources:
            for text in [q] + [f"{q} in {loc}" for loc in locations]:
                out[query_id("web", text)] = new_query("web", "web", text)
        if "maps" in sources:
            for text in [f"{q} in {loc}" for loc in locations] or [q]:
                out[query_id("maps", text)] = new_query("maps", "maps", text)
    if "lists" in sources:
        for q in queries.list_queries:
            out[query_id("lists", q)] = new_query("lists", "web", q)
    return out


def nearby_queries(queries: QueryFile, town: str) -> dict[str, dict]:
    return {query_id(f"nearby-{kind}", f"{q} near {town}"): new_query("nearby", kind, f"{q} near {town}")
            for q in queries.nearby_queries for kind in ("maps", "web")}


def settle(query: dict, candidates: dict[str, dict]) -> bool:
    """Once its companies are classified, decide whether a query's next page is due: only if the last page
    found at least one new in-market company. Returns False while some are still unclassified."""
    found = [candidates[k] for k in query["keys"] if k in candidates]
    if any(c.get("verdict") in (None, "error") for c in found):
        return False
    productive = any(c["verdict"] == "in" and c["round"] == query["round"] for c in found)
    query.update(settled=True, due=productive and query["page"] < MAX_PAGE)
    return True


def should_stop(new_in: int, total_in: int) -> bool:
    return new_in == 0 or new_in < STOP_SHARE * total_in


def add_found_by(candidate: dict, source: str, detail: str) -> None:
    entry = {"source": source, "detail": detail}
    if entry not in candidate["found_by"]:
        candidate["found_by"].append(entry)


def sources_of(candidate: dict) -> set[str]:
    return {f["source"] for f in candidate["found_by"]}


def is_maps(found: dict) -> bool:
    return found["source"] == "maps" or found["detail"].startswith("maps:")


def state_path(market_id: str, blind: bool = False) -> Path:
    return DISCOVERY_DIR / f"{market_id}{'.blind' if blind else ''}.json"


def load_state(market_id: str, blind: bool = False) -> dict | None:
    path = state_path(market_id, blind)
    return json.loads(path.read_text()) if path.exists() else None


def fresh_state(market_id: str, blind: bool) -> dict:
    return {"market_id": market_id, "blind": blind, "round": 0, "seeded": False, "candidates": {}, "queries": {},
            "towns": [], "snowballed": [], "lists_read": [], "unresolved": {}, "rounds": [], "runs": []}


# The discovery run


class Discovery:
    def __init__(self, market: Market, blind: bool = False, sources: set[str] = set(SOURCES),
                 max_cost: float = MAX_COST, reclassify: bool = False, concurrency: int = 16):
        self.market, self.blind, self.max_cost, self.reclassify = market, blind, max_cost, reclassify
        self.sources = sources - {"seed"} if blind else sources
        self.queries = load_queries(market.id)
        self.state = load_state(market.id, blind) or fresh_state(market.id, blind)
        self.candidates: dict[str, dict] = self.state["candidates"]
        self.names = {norm_name(c["name"]): k for k, c in self.candidates.items() if norm_name(c["name"])}
        self.seed_keys = {c.id for c in load_companies()}
        self.prompt_hash = hashlib.sha1((system_prompt(market.id) + role_prompt(market.id)).encode()).hexdigest()[:12]
        self.classifier = RoleClassifier(concurrency)
        self.fetcher = self.classifier.fetcher
        self.llm_limit = asyncio.Semaphore(concurrency)
        self.started = time.time()
        self.spend = Counter()   # tokens by model, LLM calls, dropped leads; searches come from the fetcher
        self.stopped_on_budget = False
        self.last_progress = 0.0

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc):
        await self.classifier.__aexit__(*exc)

    # Spend

    def cost(self) -> float:
        s = self.spend
        return (self.fetcher.searches * PRICE_SEARCH
                + (s["haiku_in"] * PRICE_IN + s["haiku_out"] * PRICE_OUT
                   + s["sonnet_in"] * PRICE_SONNET_IN + s["sonnet_out"] * PRICE_SONNET_OUT) / 1e6)

    def over_budget(self) -> bool:
        if self.cost() >= self.max_cost:
            self.stopped_on_budget = True
        return self.stopped_on_budget

    def progress(self, text: str) -> None:
        if time.time() - self.last_progress < 1:
            return
        self.last_progress = time.time()
        print(f"\r{self.market.id} round {self.state['round']}: {text} (${self.cost():.2f})".ljust(100),
              end="", file=sys.stderr, flush=True)

    async def ask(self, model: str, system: str, user: str, schema: type[BaseModel], max_tokens: int = 8000):
        """One structured LLM call, cached by its full input. None if it failed."""
        key = f"{model}|{system}|{user}|{schema.__name__}"
        if cached := cache_get("llm", key):
            return schema.model_validate(cached)
        sonnet = model == SONNET
        try:
            async with self.llm_limit:
                response = await self.classifier.llm.messages.parse(
                    model=model, max_tokens=max_tokens, system=system,
                    messages=[{"role": "user", "content": user}],
                    output_config={"effort": SONNET_EFFORT if sonnet else EFFORT}, output_format=schema)
        except (anthropic.APIError, httpx.HTTPError, ValueError) as e:   # ValueError: output cut off at max_tokens
            self.spend["llm_errors"] += 1
            print(f"\n{type(e).__name__}: {e}"[:300], file=sys.stderr)
            return None
        tier = "sonnet" if sonnet else "haiku"
        self.spend[f"{tier}_in"] += response.usage.input_tokens
        self.spend[f"{tier}_out"] += response.usage.output_tokens
        self.spend["llm_calls"] += 1
        if response.parsed_output is None:
            return None
        cache_put("llm", key, response.parsed_output.model_dump())
        return response.parsed_output

    # Sources

    def seed_leads(self) -> list[Lead]:
        leads = [Lead(e.name, e.url, None, "seed", "examples_in") for e in self.market.examples_in
                 if company_key(lead_url(e.url) or e.url) not in self.candidates]
        if "seed" in self.sources and not self.state["seeded"]:
            leads += [Lead(c.name, c.url, None, "seed", "data/pac_companies.json") for c in load_companies()]
            self.state["seeded"] = True
        return leads

    async def run_query(self, qid: str) -> list[Lead]:
        """The next page of one web or maps query. For list queries, each result page goes to the list reader."""
        query = self.state["queries"][qid]
        if self.over_budget():
            return []
        page = query["page"] + 1
        label = f"{query['kind']}: {query['q']}" + (f" (page {page})" if page > 1 else "")
        try:
            if query["kind"] == "maps":
                results = (await self.fetcher.places(query["q"], page))["results"]
                leads = [Lead(p["title"], p["website"], parse_town(p["address"]) or p["address"] or None,
                              query["source"], label, qid) for p in results if p["title"]]
            else:
                results = (await self.fetcher.web_page(query["q"], page))["results"]
                leads = [Lead(title_name(r["title"], r["link"]), r["link"], None, query["source"], label, qid)
                         for r in results if r["link"]]
        except httpx.HTTPError as e:
            self.spend["search_errors"] += 1
            print(f"\nsearch failed: {query['q']}: {type(e).__name__} {e}"[:300], file=sys.stderr)
            return []
        query.update(page=page, round=self.state["round"], keys=[], settled=False, due=False)
        if query["source"] == "lists":
            pages = await asyncio.gather(*(self.read_list(lead.url, "lists", qid) for lead in leads))
            leads += [lead for found in pages for lead in found]
        return leads

    async def read_list(self, url: str, source: str, qid: str | None = None, depth: int = 0) -> list[Lead]:
        """Every company a page lists. Up to MORE_PAGES more pages of the same list are read once, one level deep."""
        if url in self.state["lists_read"] or self.over_budget():
            return []
        self.state["lists_read"].append(url)
        page = await self.fetcher.list_page(url)
        if not page["text"]:
            self.spend["lists_empty"] += 1
            return []
        chunks = [page["text"][i:i + LIST_CHUNK_CHARS] for i in range(0, len(page["text"]), LIST_CHUNK_CHARS)]
        answers = [a for found in await asyncio.gather(*(self.read_chunk(page["final_url"], c) for c in chunks[:LIST_CHUNKS]))
                   for a in found]
        site = company_key(page["final_url"] or url)
        leads, more = [], []
        for answer in filter(None, answers):
            for c in answer.companies:
                own = lead_url(c.url)
                if own and company_key(own) == site:   # a profile page on the list's own site, not the company's
                    own = None
                leads.append(Lead(c.name, own, c.location, source, f"list: {page['final_url']}", qid))
            more += [u for u in answer.more_pages if u.startswith("http") and company_key(u) == site]
        if depth == 0:
            for found in await asyncio.gather(*(self.read_list(u, source, qid, 1) for u in list(dict.fromkeys(more))[:MORE_PAGES])):
                leads += found
        return leads

    async def read_chunk(self, url: str, text: str) -> list[ListPage]:
        """The list reader on one chunk. A chunk listing too many companies for one answer is read in halves."""
        answer = await self.ask(MODEL, (PROMPTS / "read_list.md").read_text(), f"Page: {url}\n\n{text}", ListPage,
                                max_tokens=16000)
        if answer is None and len(text) > LIST_CHUNK_CHARS / 8:
            half = len(text) // 2
            return [a for part in (text[:half], text[half:]) for a in await self.read_chunk(url, part)]
        return [answer] if answer else []

    async def snowball(self, key: str) -> list[Lead]:
        """An in-market company's homepage, plus up to SNOWBALL_PAGES list pages from one site search."""
        if self.over_budget():
            return []
        self.state["snowballed"].append(key)
        candidate = self.candidates[key]
        if is_social(candidate["url"]):
            return []
        terms = " OR ".join(f'"{t}"' for t in self.queries.list_terms)
        try:
            results = (await self.fetcher.web_page(f"site:{key} ({terms})"))["results"]
        except httpx.HTTPError:
            results = []
        pages = [root_url(candidate["url"])] + [r["link"] for r in results[:SNOWBALL_PAGES] if r["link"]]
        found = await asyncio.gather(*(self.read_list(u, "snowball") for u in dict.fromkeys(pages)))
        return [lead for leads in found for lead in leads]

    async def model_leads(self) -> list[Lead]:
        if self.over_budget():
            return []
        known = [f"{e.name} ({e.url})" for e in self.market.examples_in]
        known += [f"{c['name']} ({c['url']}{', ' + c['location'] if c.get('location') else ''})"
                  for c in self.candidates.values() if c.get("verdict") == "in"]
        user = "Companies already on the list:\n\n" + "\n".join(f"- {k}" for k in dict.fromkeys(known))
        answer = await self.ask(SONNET, more_prompt(self.market.id), user, CompanyList, max_tokens=16000)
        detail = f"round {self.state['round']}"
        return [Lead(c.name, lead_url(c.url), c.location, "model", detail) for c in (answer.companies if answer else [])]

    # Leads -> candidates

    async def resolve(self, lead: Lead) -> str | None:
        """One search for a lead without a website, and one small call to pick its own site or social page."""
        query = f'"{lead.name}" {parse_town(lead.location) or ""}'.strip()
        try:
            results = (await self.fetcher.web_page(query))["results"]
        except httpx.HTTPError:
            return None
        if not results:
            return None
        lines = [f"Company: {lead.name}", f"Found: {lead.detail}" + (f", {lead.location}" if lead.location else ""),
                 "", f"Search results for: {query}", ""]
        lines += [f"{i}. {r['title']} ({r['link']})\n   {r['snippet']}" for i, r in enumerate(results, 1)]
        pick = await self.ask(MODEL, (PROMPTS / "resolve_lead.md").read_text(), "\n".join(lines), Pick, max_tokens=2000)
        links = {company_key(r["link"]) for r in results if r["link"]}
        url = lead_url(pick.url) if pick else None
        return url if url and company_key(url) in links else None

    async def add_leads(self, leads: list[Lead]) -> int:
        """Resolve leads without a website, then dedupe by company key. Returns the number of new candidates."""
        by_name: dict[str, list[Lead]] = {}
        for lead in leads:
            lead.url = lead_url(lead.url)
            if not lead.url and lead.name.strip():
                by_name.setdefault(norm_name(lead.name), []).append(lead)
        to_resolve = [n for n in by_name if n and n not in self.names and n not in self.state["unresolved"]]
        done = 0

        async def one(n):
            nonlocal done
            url = None if self.over_budget() else await self.resolve(by_name[n][0])
            done += 1
            self.progress(f"resolving {done}/{len(to_resolve)} leads without a website")
            return n, url

        for n, url in await asyncio.gather(*(one(n) for n in to_resolve)):
            if url:
                for lead in by_name[n]:
                    lead.url = url
            elif not self.stopped_on_budget:
                self.state["unresolved"][n] = by_name[n][0].name
        for n, group in by_name.items():
            if n and n in self.names:
                for lead in group:
                    lead.url = self.candidates[self.names[n]]["url"]
        new = 0
        for lead in leads:
            if not lead.url:
                continue
            key = company_key(lead.url)
            if key not in self.candidates:
                self.candidates[key] = {"company_id": key, "name": lead.name.strip() or key, "url": lead.url,
                                        "location": None, "round": self.state["round"], "seed": key in self.seed_keys,
                                        "found_by": []}
                if norm_name(lead.name):
                    self.names.setdefault(norm_name(lead.name), key)
                new += 1
            candidate = self.candidates[key]
            add_found_by(candidate, lead.source, lead.detail)
            if lead.location and not candidate["location"]:
                candidate["location"] = parse_town(lead.location) or lead.location
            if lead.query and key not in self.state["queries"][lead.query]["keys"]:
                self.state["queries"][lead.query]["keys"].append(key)
        return new

    # Classify and locate

    async def classify_pending(self) -> None:
        pending = [c for c in self.candidates.values() if c.get("verdict") in (None, "error")]
        done = 0

        async def one(c):
            nonlocal done
            if not self.over_budget():
                c.update({k: v for k, v in (await self.two_stage(c)).items() if k in VERDICT_FIELDS})
            done += 1
            self.progress(f"classifying {done}/{len(pending)}")

        await asyncio.gather(*(one(c) for c in pending))

    async def two_stage(self, c: dict) -> dict:
        """Both stages, unchanged. Results are cached by prompt version, so the blind run and re-runs reuse them."""
        key = f"{self.market.id}|{self.prompt_hash}|{c['url']}"
        if not self.reclassify and (cached := cache_get("verdicts", key)):
            return cached
        r = await self.classifier.two_stage(Company(id=c["company_id"], name=c["name"], url=c["url"]), self.market)
        self.spend["haiku_in"] += r.get("input_tokens", 0) + (r.get("role_input_tokens") or 0)
        self.spend["haiku_out"] += r.get("output_tokens", 0) + (r.get("role_output_tokens") or 0)
        self.spend["classified"] += 1
        if r["verdict"] != "error" and r.get("role") != "error":
            cache_put("verdicts", key, r)
        return r

    async def locate(self) -> None:
        """One map lookup by name for each in-market company without a known town."""
        todo = [c for c in self.candidates.values()
                if c.get("verdict") == "in" and not c.get("location") and not c.get("located")]

        async def one(c):
            if self.over_budget():
                return
            try:
                places = (await self.fetcher.places(c["name"]))["results"]
            except httpx.HTTPError:
                return
            c["located"] = True
            for p in places:
                same_site = p["website"] and lead_url(p["website"]) and company_key(lead_url(p["website"])) == c["company_id"]
                a, b = norm_name(p["title"]), norm_name(c["name"])
                if same_site or (a and b and (a in b or b in a)):
                    c["location"] = parse_town(p["address"])
                    return

        await asyncio.gather(*(one(c) for c in todo))

    # Rounds

    def in_market(self) -> list[dict]:
        return [c for c in self.candidates.values() if c.get("verdict") == "in"]

    def ensure_queries(self) -> None:
        """Add the query file's queries that aren't in the state yet (all of them on a fresh run)."""
        locations = self.market.geography.search_locations if self.market.geography else []
        for qid, query in first_queries(self.queries, locations, self.sources).items():
            self.state["queries"].setdefault(qid, query)

    def expand(self) -> None:
        """Nearby searches around each new town with an in-market company."""
        if "nearby" not in self.sources:
            return
        for c in self.in_market():
            town = parse_town(c.get("location"))
            if town and town not in self.state["towns"]:
                self.state["towns"].append(town)
                for qid, query in nearby_queries(self.queries, town).items():
                    self.state["queries"].setdefault(qid, query)

    async def round(self) -> dict:
        self.state["round"] += 1
        r, t0, searches0, cost0 = self.state["round"], time.time(), self.fetcher.searches, self.cost()
        self.ensure_queries()
        self.expand()
        due = [qid for qid, q in self.state["queries"].items() if q["due"] and q["settled"] and q["source"] in self.sources]
        snow = [c["company_id"] for c in self.in_market() if c["company_id"] not in self.state["snowballed"]] \
            if "snowball" in self.sources else []
        jobs = [self.run_query(qid) for qid in due] + [self.snowball(k) for k in snow]
        if "model" in self.sources:
            jobs.append(self.model_leads())
        done = 0

        async def one(job):
            nonlocal done
            try:
                leads = await job
            except Exception as e:   # one failed job must not lose the round
                self.spend["job_errors"] += 1
                print(f"\njob failed: {type(e).__name__}: {e}"[:300], file=sys.stderr)
                leads = []
            done += 1
            self.progress(f"searching {done}/{len(jobs)}")
            return leads

        leads = self.seed_leads() + [lead for found in await asyncio.gather(*(one(j) for j in jobs)) for lead in found]
        new = await self.add_leads(leads)
        self.save()
        await self.classify_pending()
        await self.locate()
        for q in self.state["queries"].values():
            if not q["settled"]:
                settle(q, self.candidates)
        new_in = [c for c in self.in_market() if c["round"] == r]
        stats = {
            "round": r, "queries": len(due), "snowballed": len(snow), "leads": len(leads), "new_candidates": new,
            "new_in": len(new_in), "total_in": len(self.in_market()),
            "new_in_by_source": dict(Counter(s for c in new_in for s in sources_of(c))),
            "searches": self.fetcher.searches - searches0, "cost": round(self.cost() - cost0, 2),
            "seconds": round(time.time() - t0), "stopped_on_budget": self.stopped_on_budget,
        }
        self.state["rounds"].append(stats)
        print(file=sys.stderr)
        print(f"round {r}: {stats['leads']} leads, {new} new candidates, {len(new_in)} new in-market "
              f"({stats['total_in']} total), ${stats['cost']:.2f}", file=sys.stderr)
        return stats

    async def run(self, rounds: int = ROUNDS) -> None:
        for _ in range(rounds):
            stats = await self.round()
            self.save()
            if self.stopped_on_budget or should_stop(stats["new_in"], stats["total_in"]):
                break
        self.finish("discover")

    def finish(self, command: str) -> None:
        self.state["runs"].append({
            "command": command, "sources": sorted(self.sources), "rounds": self.state["round"],
            "searches": self.fetcher.searches, "llm_calls": self.spend["llm_calls"], "classified": self.spend["classified"],
            "llm_errors": self.spend["llm_errors"], "search_errors": self.spend["search_errors"],
            "job_errors": self.spend["job_errors"],
            "cost": round(self.cost(), 2), "minutes": round((time.time() - self.started) / 60, 1),
            "max_cost": self.max_cost, "stopped_on_budget": self.stopped_on_budget,
        })
        self.save()

    def save(self) -> None:
        path = state_path(self.market.id, self.blind)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(self.state, indent=1, ensure_ascii=False) + "\n")

    # The probe

    async def probe(self, n: int = PROBE_QUERIES, pages: int = PROBE_PAGES, seed: int | None = None) -> dict:
        """Fresh-eyes check: new searches discovery has never run, in random states, on web and maps, a few pages
        deep. Reports what share of the in-market companies they find was already on the list, then adds them."""
        already = "\n".join(f"- {q}" for q in self.queries.company_queries + self.queries.list_queries)
        existing = ("# Searches already run\n\nThese searches have already been run. Write different ones: new "
                    "phrasings, other names for the product and for the companies, other kinds of companies that "
                    "rules A, B, and C cover.\n\n" + already)
        answer = await self.ask(SONNET, queries_prompt(self.market.id, existing), "Write the searches.", QueryFile)
        if answer is None:
            raise SystemExit("The probe's searches could not be written (LLM error).")
        rng = random.Random(seed)
        locations = (self.market.geography.search_locations if self.market.geography else []) or [""]
        searches = [(q, rng.choice(locations)) for q in answer.company_queries[:n]]
        before = {c["company_id"] for c in self.in_market()}
        self.state["round"] += 1
        texts = [f"{q} in {loc}" if loc else q for q, loc in searches]
        found_by: dict[str, list[str]] = {}
        found = await asyncio.gather(*(self.probe_page(kind, text, page) for text in texts
                                       for kind in ("web", "maps") for page in range(1, pages + 1)))
        all_leads = [lead for group in found for lead in group]
        await self.add_leads(all_leads)
        for lead in all_leads:
            if lead.url:
                found_by.setdefault(company_key(lead.url), []).append(lead.detail)
        await self.classify_pending()
        await self.locate()
        probe_in = {k for k in found_by if self.candidates.get(k, {}).get("verdict") == "in"}
        result = {
            "searches": texts, "pages": pages,
            "in_found": len(probe_in), "already": len(probe_in & before),
            "misses": [{"company_id": k, "name": self.candidates[k]["name"], "url": self.candidates[k]["url"],
                        "location": self.candidates[k].get("location"), "found_by": found_by[k][:3]}
                       for k in sorted(probe_in - before)],
            "candidates": len(found_by),
        }
        self.state.setdefault("probes", []).append(result)
        self.finish("probe")
        return result

    async def probe_page(self, kind: str, text: str, page: int) -> list[Lead]:
        label = f"{kind}: {text}" + (f" (page {page})" if page > 1 else "")
        try:
            if kind == "maps":
                return [Lead(p["title"], p["website"], parse_town(p["address"]) or p["address"] or None, "probe", label)
                        for p in (await self.fetcher.places(text, page))["results"] if p["title"]]
            return [Lead(title_name(r["title"], r["link"]), r["link"], None, "probe", label)
                    for r in (await self.fetcher.web_page(text, page))["results"] if r["link"]]
        except httpx.HTTPError:
            self.spend["search_errors"] += 1
            return []


async def write_queries(market: Market) -> QueryFile:
    """The first version of markets/<id>.discovery.json, from the brief (one Sonnet call)."""
    llm = anthropic.AsyncAnthropic(max_retries=4)
    try:
        response = await llm.messages.parse(
            model=SONNET, max_tokens=8000, system=queries_prompt(market.id, ""),
            messages=[{"role": "user", "content": "Write the searches."}],
            output_config={"effort": SONNET_EFFORT}, output_format=QueryFile)
    finally:
        await llm.close()
    if response.parsed_output is None:
        raise SystemExit(f"No query file (stop_reason={response.stop_reason})")
    queries_path(market.id).write_text(json.dumps(response.parsed_output.model_dump(), indent=2, ensure_ascii=False) + "\n")
    return response.parsed_output


# Outputs: leads sheet and report

LEAD_COLUMNS = ["company_id", "name", "url", "location", "role", "rule", "reason", "evidence_url", "role_reason",
                "customer_evidence_url", "competitor_evidence_url", "sources", "found_by", "round", "seed"]


def write_leads(market_id: str, state: dict) -> Path:
    path = EVAL_DIR / f"leads_{market_id}.csv"
    rows = sorted((c for c in state["candidates"].values() if c.get("verdict") == "in"),
                  key=lambda c: (state_of(c.get("location")) or "~", c["name"].lower()))
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=LEAD_COLUMNS, extrasaction="ignore")
        writer.writeheader()
        for c in rows:
            writer.writerow({**c, "sources": ", ".join(sorted(sources_of(c))),
                             "found_by": "; ".join(f["detail"] for f in c["found_by"][:3])})
    return path


def seed_in_ids(market_id: str) -> set[str]:
    """Seed-list companies M1 calls in: from the full run if there is one, else from M2's full run."""
    if full := load_state(market_id):
        ids = {k for k, c in full["candidates"].items() if c["seed"] and c.get("verdict") == "in"}
        if ids:
            return ids
    path = EVAL_DIR / f"roles_{market_id}.csv"
    with open(path, newline="", encoding="utf-8") as f:
        return {r["company_id"] for r in csv.DictReader(f) if r["verdict"] == "in"}


def report(market: Market, state: dict) -> str:
    cands = state["candidates"]
    ins = [c for c in cands.values() if c.get("verdict") == "in"]
    roles = Counter(c.get("role") for c in ins)
    seed_in = seed_in_ids(market.id)
    run = state["runs"][-1] if state["runs"] else {}
    last = state["rounds"][-1] if state["rounds"] else {}

    def pct(a, b):
        return f"{a / b:.0%}" if b else "n/a"

    title = "Blind discovery run (no seed list)" if state["blind"] else "Discovery"
    lines = [f"# {title}: {market.name} (`{market.id}`)", ""]
    if run.get("stopped_on_budget"):
        lines += [f"**This run stopped on its budget (${run['max_cost']:.0f}) before finishing.** Work still due is "
                  f"listed under 'Left to do'; run `signal discover` again to continue.", ""]
    discovered = [c for c in ins if not c["seed"]]
    lines += [
        "## Headline", "",
        f"**{len(ins)} in-market companies**: {roles['customer']} customer, {roles['both']} both, "
        f"{roles['competitor']} competitor, {roles['neither']} neither"
        + (f", {roles['error']} role errors" if roles["error"] else "") + ".",
        "",
        f"That is **{len(ins) / len(seed_in):.1f}x** the {len(seed_in)} in-market companies on the seed list. "
        f"{len(discovered)} of them are not on the seed list at all." if seed_in else "",
        "",
    ]
    if state["blind"]:
        refound = [k for k in seed_in if k in cands]
        missed = sorted(k for k in seed_in if k not in cands)
        out_now = [k for k in refound if cands[k].get("verdict") != "in"]
        lines += [
            "## Floor: re-finding the seed list", "",
            f"Re-found {len(refound)} of the {len(seed_in)} in-market seed companies ({pct(len(refound), len(seed_in))}) "
            f"without the seed list. {len(out_now)} of those re-found were judged differently this time "
            "(M1 run-to-run variance, not a discovery miss).", "",
        ]
        if missed:
            lines += ["Missed (never surfaced by any source):", ""]
            names = {r["company_id"]: r["name"] for r in _roles_rows(market.id)}
            lines += [f"- {names.get(k, k)} (`{k}`)" for k in missed]
            lines.append("")
        if out_now:
            lines += ["Re-found but judged differently this run:", ""]
            lines += [f"- {cands[k]['name']} (`{k}`): {cands[k].get('verdict')}. {cands[k].get('reason', '')}" for k in out_now]
            lines.append("")

    by_source = {s: [c for c in cands.values() if s in sources_of(c)] for s in (*SOURCES, "probe")}
    lines += ["## By source", "",
              "| Source | Candidates | In market | Customer | Both | Competitor | Neither | Only this source |",
              "|---|---|---|---|---|---|---|---|"]
    for s, cs in by_source.items():
        if not cs:
            continue
        cin = [c for c in cs if c.get("verdict") == "in"]
        r = Counter(c.get("role") for c in cin)
        only = sum(1 for c in cin if sources_of(c) == {s})
        lines.append(f"| {s} | {len(cs)} | {len(cin)} | {r['customer']} | {r['both']} | {r['competitor']} | {r['neither']} | {only} |")
    lines.append("")

    lines += ["## Rounds (saturation curve)", "",
              "| Round | Queries run | Snowballed | Leads | New candidates | New in market | % of list | Cost | Minutes |",
              "|---|---|---|---|---|---|---|---|---|"]
    for r in state["rounds"]:
        lines.append(f"| {r['round']} | {r['queries']} | {r['snowballed']} | {r['leads']} | {r['new_candidates']} | "
                     f"{r['new_in']} | {pct(r['new_in'], r['total_in'])} | ${r['cost']:.2f} | {r['seconds'] / 60:.0f} |")
    lines += ["", f"Last round added {pct(last.get('new_in', 0), last.get('total_in', 0))} new in-market companies "
              f"(stop rule: under {STOP_SHARE:.0%})." if last else "", ""]

    queries = [q for q in state["queries"].values() if q["page"]]
    depth = Counter(q["page"] for q in queries)
    lines += ["## Paging depth", "",
              f"{len(queries)} queries ran. Deepest page reached per query: "
              + ", ".join(f"page {p}: {n}" for p, n in sorted(depth.items())) + ".",
              f" {sum(1 for q in state['queries'].values() if q['due'])} queries still have a productive next page.", ""]
    deep = sorted(queries, key=lambda q: -q["page"])[:10]
    lines += [f"- `{q['kind']}: {q['q']}`: {q['page']} pages" for q in deep if q["page"] > 1]
    lines += ["", f"Towns searched with nearby queries: {len(state['towns'])}.", ""]

    multi = sum(1 for c in ins if len(sources_of(c) - {'seed'}) >= 2)
    maps_ = {c["company_id"] for c in ins if any(is_maps(f) for f in c["found_by"])}
    other = {c["company_id"] for c in ins if any(not is_maps(f) for f in c["found_by"])}
    both = maps_ & other
    estimate = f"about {len(maps_) * len(other) / len(both):.0f}" if both else "n/a (no overlap)"
    lines += [
        "## Source overlap and market size", "",
        f"- In-market companies found by two or more sources (not counting the seed list): {multi} of {len(ins)} ({pct(multi, len(ins))}).",
        f"- Maps (map search, including nearby map searches) found {len(maps_)}; everything else found {len(other)}; both found {len(both)}.",
        f"- Capture-recapture estimate of the reachable market: {estimate} in-market companies (we have {len(ins)}).",
        "",
    ]

    states = Counter(state_of(c.get("location")) for c in ins)
    home = {STATE_CODES.get(loc.lower()) for loc in (market.geography.search_locations if market.geography else [])}
    outside = sum(n for s, n in states.items() if s and home and s not in home)
    lines += ["## By state", "",
              f"Location known for {len(ins) - states[None]} of {len(ins)} in-market companies. "
              f"Outside the search locations (shown, not filtered): {outside}.", "",
              ", ".join(f"{s} {n}" for s, n in sorted(states.items(), key=lambda x: (-x[1], x[0] or "")) if s), ""]

    unresolved = state["unresolved"]
    lines += ["## Leads dropped: no website found", "",
              f"{len(unresolved)} names from lists, maps, or the model had no website or social page in one search."
              + (" Examples: " + "; ".join(list(unresolved.values())[:30]) + "." if unresolved else ""), ""]

    due = [q for q in state["queries"].values() if q["due"]]
    snow_left = sum(1 for c in ins if c["company_id"] not in state["snowballed"])
    unclassified = sum(1 for c in cands.values() if c.get("verdict") in (None, "error"))
    lines += ["## Left to do", "",
              f"Queries with a next page due: {len(due)}. In-market companies not yet snowballed: {snow_left}. "
              f"Candidates not yet classified (or errors): {unclassified}.", ""]

    lines += ["## Runs", "", "| Command | Sources | Searches | LLM calls | Classified | Cost | Minutes | Stopped on budget |",
              "|---|---|---|---|---|---|---|---|"]
    for r in state["runs"]:
        lines.append(f"| {r['command']} | {', '.join(r['sources'])} | {r['searches']} | {r['llm_calls']} | {r['classified']} | "
                     f"${r['cost']:.2f} | {r['minutes']} | {'yes' if r['stopped_on_budget'] else 'no'} |")
    lines += ["", f"Total candidates: {len(cands)}. Verdicts: "
              + ", ".join(f"{v} {n}" for v, n in Counter(c.get('verdict') for c in cands.values()).most_common()) + ".", ""]
    return "\n".join(lines)


def _roles_rows(market_id: str) -> list[dict]:
    path = EVAL_DIR / f"roles_{market_id}.csv"
    if not path.exists():
        return []
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def probe_report(market: Market, result: dict) -> str:
    share = result["already"] / result["in_found"] if result["in_found"] else None
    lines = [
        f"# Probe: {market.name} (`{market.id}`)", "",
        f"{len(result['searches'])} fresh searches discovery has never run, on web and maps, {result['pages']} pages each. "
        f"They found {result['candidates']} candidates, {result['in_found']} of them in the market.", "",
        f"**Already on the list: {result['already']} of {result['in_found']}"
        + (f" ({share:.0%})" if share is not None else "") + "** (target: at least 95%). "
        "The new ones below have now been added to the list.", "",
        "## Searches", "", *[f"- {s}" for s in result["searches"]], "",
        "## In-market companies the list was missing", "",
    ]
    lines += [f"- **{m['name']}** ({m['url']}{', ' + m['location'] if m.get('location') else ''}): found by "
              + "; ".join(m["found_by"]) for m in result["misses"]] or ["None."]
    return "\n".join(lines) + "\n"
