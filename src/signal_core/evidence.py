"""Evidence for the classifiers: the company's homepage text and one Serper site search (stage 1),
plus one Serper search for products like ours (stage 2). Discovery (M3) adds paged web search,
Serper places (map) search, and page text with its links for the list reader.

Every fetch and search result is cached in .cache/ so re-runs only pay for LLM calls.
Delete .cache/ (or a subfolder) to refetch.
"""

import asyncio
import hashlib
import json
import os
import re
from urllib.parse import urljoin, urlsplit

import httpx
from selectolax.lexbor import LexborHTMLParser

from signal_core.companies import Company, company_key
from signal_core.markets import ROOT, Market

CACHE_DIR = ROOT / ".cache"
PAGE_CHARS = 6000
SEARCH_RESULTS = 10
# Google ignores query words past the 32nd, so terms beyond that are left out.
MAX_QUERY_WORDS = 32
# Discovery: the list reader reads up to LIST_CHUNKS chunks of LIST_CHUNK_CHARS characters per page.
LIST_CHUNK_CHARS = 40_000
LIST_CHUNKS = 5
USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/130.0 Safari/537.36"
)


def _cache_path(kind: str, key: str):
    return CACHE_DIR / kind / (hashlib.sha1(key.encode()).hexdigest() + ".json")


def cache_get(kind: str, key: str) -> dict | None:
    path = _cache_path(kind, key)
    return json.loads(path.read_text()) if path.exists() else None


def cache_put(kind: str, key: str, value: dict) -> dict:
    path = _cache_path(kind, key)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False))
    return value


def page_text(html: str, limit: int = PAGE_CHARS) -> str:
    """Title, meta description, and visible text, whitespace collapsed and capped."""
    tree = LexborHTMLParser(html)
    title = tree.css_first("title")
    meta = tree.css_first('meta[name="description"]') or tree.css_first('meta[property="og:description"]')
    tree.strip_tags(["script", "style", "noscript", "svg", "template", "iframe"])
    parts = [
        title.text(strip=True) if title else "",
        (meta.attributes.get("content") or "") if meta else "",
        tree.body.text(separator=" ", strip=True) if tree.body else "",
    ]
    return re.sub(r"\s+", " ", " | ".join(p for p in parts if p)).strip()[:limit]


def text_with_links(html: str, base_url: str, limit: int = LIST_CHUNK_CHARS * LIST_CHUNKS) -> str:
    """Title and visible text with each link written inline after its text: `Acme Co [https://acme.com]`."""
    tree = LexborHTMLParser(html)
    title = tree.css_first("title")
    tree.strip_tags(["script", "style", "noscript", "svg", "template", "iframe"])
    for a in tree.css("a"):
        href = (a.attributes.get("href") or "").strip()
        text = a.text(separator=" ", strip=True)
        if href and not href.startswith(("#", "javascript:", "tel:")):
            a.replace_with(f" {text} [{urljoin(base_url, href)}] ")
        else:
            a.replace_with(f" {text} ")
    parts = [title.text(strip=True) if title else "", tree.body.text(separator=" ", strip=True) if tree.body else ""]
    return re.sub(r"\s+", " ", " | ".join(p for p in parts if p)).strip()[:limit]


def root_url(url: str) -> str:
    parts = urlsplit(url)
    return f"{parts.scheme}://{parts.netloc}/"


def search_query(company: Company, market: Market) -> str:
    """site:<domain> plus the market's terms OR'ed together. Social pages search by name instead."""
    return _scoped_query(company, market.end_product.terms + market.our_products.terms)


def product_search_query(company: Company, market: Market) -> str | None:
    """Like search_query, but only the terms for products like ours (stage 2). None if the brief has none."""
    return _scoped_query(company, market.our_products.terms) if market.our_products.terms else None


def _scoped_query(company: Company, all_terms: list[str]) -> str:
    scope = f'"{company.name}"' if company.is_social else f"site:{company_key(company.url)}"
    words = len(scope.split())
    terms = []
    for term in all_terms:
        n = len(term.split())
        if words + n > MAX_QUERY_WORDS:
            break
        terms.append(f'"{term}"')
        words += n
    return f"{scope} ({' OR '.join(terms)})"


class Fetcher:
    """Shared HTTP client for page fetches and Serper searches, with a cap on requests in flight."""

    def __init__(self, concurrency: int = 16):
        self.limit = asyncio.Semaphore(concurrency)
        self.http = httpx.AsyncClient(
            headers={"User-Agent": USER_AGENT, "Accept-Language": "en-US,en;q=0.9"},
            follow_redirects=True,
            timeout=httpx.Timeout(20.0, connect=10.0),
            transport=httpx.AsyncHTTPTransport(retries=1),
        )
        self.serper_key = os.environ.get("SERPER_API_KEY")
        self.searches = 0

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc):
        await self.http.aclose()

    async def page(self, url: str) -> dict:
        if cached := cache_get("pages", url):
            return cached
        async with self.limit:
            try:
                r = await self.http.get(url)
                content_type = r.headers.get("content-type", "")
                html = "html" in content_type or not content_type
                result = {"url": url, "final_url": str(r.url), "status": r.status_code,
                          "text": page_text(r.text) if html else "", "error": None}
            except (httpx.HTTPError, UnicodeDecodeError) as e:
                result = {"url": url, "final_url": None, "status": None, "text": "",
                          "error": f"{type(e).__name__}: {e}"[:200]}
        return cache_put("pages", url, result)

    async def homepage(self, url: str) -> dict:
        """The company URL; if that fails, its site root; if the site doesn't answer on https, http."""
        page = await self.page(url)
        if page["status"] and page["status"] < 400:
            return page
        candidates = [root_url(url)]
        if url.startswith("https://"):
            candidates.append(root_url("http://" + url.removeprefix("https://")))
        for candidate in candidates:
            if candidate == url:
                continue
            fallback = await self.page(candidate)
            if fallback["status"] and fallback["status"] < 400:
                return fallback
            if page["status"] is None and fallback["status"] is not None:
                page = fallback
        return page

    async def search(self, query: str) -> dict:
        if cached := cache_get("search", query):
            return cached
        if not self.serper_key:
            raise SystemExit("SERPER_API_KEY is not set (add it to .env)")
        async with self.limit:
            r = await self.http.post(
                "https://google.serper.dev/search",
                json={"q": query, "num": SEARCH_RESULTS},
                headers={"X-API-KEY": self.serper_key},
            )
        r.raise_for_status()
        self.searches += 1
        results = [
            {"title": o.get("title", ""), "link": o.get("link", ""), "snippet": o.get("snippet", "")}
            for o in r.json().get("organic", [])[:SEARCH_RESULTS]
        ]
        return cache_put("search", query, {"query": query, "results": results})

    async def _serper(self, endpoint: str, body: dict) -> dict:
        if not self.serper_key:
            raise SystemExit("SERPER_API_KEY is not set (add it to .env)")
        async with self.limit:
            r = await self.http.post(f"https://google.serper.dev/{endpoint}", json=body,
                                     headers={"X-API-KEY": self.serper_key})
        r.raise_for_status()
        self.searches += 1
        return r.json()

    async def web_page(self, query: str, page: int = 1) -> dict:
        """One page (10 results) of a web search. Discovery's paged search, cached apart from `search`."""
        key = f"{page}|{query}"
        if cached := cache_get("web", key):
            return cached
        data = await self._serper("search", {"q": query, "num": SEARCH_RESULTS, "page": page, "gl": "us"})
        results = [{"title": o.get("title", ""), "link": o.get("link", ""), "snippet": o.get("snippet", "")}
                   for o in data.get("organic", [])]
        return cache_put("web", key, {"query": query, "page": page, "results": results})

    async def places(self, query: str, page: int = 1) -> dict:
        """One page of a Serper places (map) search: name, address, website, category of each place."""
        key = f"{page}|{query}"
        if cached := cache_get("places", key):
            return cached
        data = await self._serper("places", {"q": query, "page": page, "gl": "us"})
        results = [{"title": o.get("title", ""), "address": o.get("address", ""), "website": o.get("website") or None,
                    "category": o.get("category", "")} for o in data.get("places", [])]
        return cache_put("places", key, {"query": query, "page": page, "results": results})

    async def list_page(self, url: str) -> dict:
        """A page's text with its links inline, for the list reader."""
        if cached := cache_get("listpages", url):
            return cached
        async with self.limit:
            try:
                r = await self.http.get(url)
                html = "html" in r.headers.get("content-type", "html")
                result = {"url": url, "final_url": str(r.url), "status": r.status_code,
                          "text": text_with_links(r.text, str(r.url)) if html and r.status_code < 400 else "", "error": None}
            except (httpx.HTTPError, UnicodeDecodeError) as e:
                result = {"url": url, "final_url": None, "status": None, "text": "", "error": f"{type(e).__name__}: {e}"[:200]}
        return cache_put("listpages", url, result)

    async def evidence(self, company: Company, market: Market) -> dict:
        query = search_query(company, market)
        if company.is_social:
            homepage = {"url": company.url, "status": None, "text": "", "error": "social page, not fetched"}
            search = await self.search(query)
        else:
            homepage, search = await asyncio.gather(self.homepage(company.url), self.search(query))
        return {"homepage": homepage, "search": search}

    async def product_search(self, company: Company, market: Market) -> dict:
        query = product_search_query(company, market)
        return await self.search(query) if query else {"query": "(no product terms in the brief)", "results": []}
