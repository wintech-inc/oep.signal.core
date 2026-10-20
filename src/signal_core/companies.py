"""Company list: load data/pac_companies.json, and build it from the CRM export (sanitize)."""

import asyncio
import csv
import json
from pathlib import Path
from urllib.parse import urlsplit

from pydantic import BaseModel

from signal_core.markets import ROOT

COMPANIES_PATH = ROOT / "data" / "pac_companies.json"
SOCIAL_HOSTS = {"facebook.com", "instagram.com"}


class CrmTag(BaseModel):
    market: str
    role: str


class Company(BaseModel):
    id: str
    name: str
    aliases: list[str] = []
    url: str
    crm: list[CrmTag] = []

    @property
    def is_social(self) -> bool:
        return is_social(self.url)


def clean_url(raw: str) -> str | None:
    """Return a usable https URL (scheme, host, path; no query or fragment), or None for junk."""
    raw = raw.strip()
    if not raw:
        return None
    # "https://a.com - https://a.com/" and "N/A - https://N/A": keep the last token.
    raw = raw.split()[-1]
    if "://" not in raw:
        raw = "https://" + raw
    parts = urlsplit(raw)
    host = (parts.hostname or "").lower()
    if parts.scheme not in ("http", "https") or "." not in host:
        return None
    return f"{parts.scheme}://{host}{parts.path}"


def bare_host(url: str) -> str:
    host = (urlsplit(url).hostname or "").lower()
    for prefix in ("www.", "m."):
        host = host.removeprefix(prefix)
    return host


def is_social(url: str) -> bool:
    return bare_host(url) in SOCIAL_HOSTS


def company_key(url: str) -> str:
    """Dedupe key: the domain without www., or host plus page path for social pages."""
    host = bare_host(url)
    if host in SOCIAL_HOSTS:
        return host + urlsplit(url).path.rstrip("/").lower()
    return host


def load_companies(path: Path = COMPANIES_PATH) -> list[Company]:
    if not path.exists():
        raise SystemExit(f"{path} not found. Run: uv run signal sanitize docs/sample_pac_companies.csv")
    return [Company.model_validate(c) for c in json.loads(path.read_text())]


def find_company(companies: list[Company], url: str) -> Company | None:
    key = company_key(clean_url(url) or url)
    return next((c for c in companies if c.id == key), None)


def merge_rows(rows: list[dict]) -> tuple[list[Company], dict]:
    """Clean and dedupe CRM rows. Returns companies (in CSV order) and what was dropped or merged."""
    by_key: dict[str, Company] = {}
    names: dict[str, list[str]] = {}
    dropped = {"no_url": [], "junk_url": []}
    for row in rows:
        name = row["company"].strip()
        raw = row["home_page"].strip()
        if not raw:
            dropped["no_url"].append(name)
            continue
        url = clean_url(raw)
        if url is None:
            dropped["junk_url"].append((name, raw))
            continue
        tags = [CrmTag(market=m.strip(), role=row["role"].strip()) for m in row["markets"].split(",") if m.strip()]
        key = company_key(url)
        names.setdefault(key, []).append(name)
        if key not in by_key:
            by_key[key] = Company(id=key, name=name, url=url, crm=tags)
            continue
        company = by_key[key]
        if name != company.name and name not in company.aliases:
            company.aliases.append(name)
        company.crm += [t for t in tags if t not in company.crm]
    merged = {key: row_names for key, row_names in names.items() if len(row_names) > 1}
    return list(by_key.values()), {**dropped, "merged": merged}


async def sanitize(csv_path: Path, check: bool = True) -> tuple[list[Company], str]:
    with open(csv_path, encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    companies, report = merge_rows(rows)

    unreachable = []
    if check:
        from signal_core.evidence import Fetcher

        async with Fetcher() as fetcher:
            sites = [c for c in companies if not c.is_social]
            pages = await asyncio.gather(*(fetcher.homepage(c.url) for c in sites))
        dead = {c.id: p["error"] for c, p in zip(sites, pages) if p["status"] is None}
        unreachable = [(c.name, c.url, dead[c.id]) for c in companies if c.id in dead]
        companies = [c for c in companies if c.id not in dead]

    return companies, _report(csv_path, len(rows), companies, report, unreachable, check)


def _report(csv_path, n_rows, companies, report, unreachable, checked) -> str:
    lines = [
        "# Sanitize report",
        "",
        f"Source: `{csv_path}` ({n_rows} rows). Output: `data/pac_companies.json` ({len(companies)} companies).",
        "",
        f"- Dropped, no URL: {len(report['no_url'])}",
        f"- Dropped, junk URL: {len(report['junk_url'])}",
        f"- Merged duplicates: {len(report['merged'])} companies had more than one row",
        f"- Dropped, site does not respond: {len(unreachable)}"
        + ("" if checked else " (site check skipped)"),
        "",
        "## Dropped: no URL",
        "",
        *[f"- {name}" for name in report["no_url"]],
        "",
        "## Dropped: junk URL",
        "",
        *[f"- {name}: `{raw}`" for name, raw in report["junk_url"]],
        "",
        "## Dropped: site does not respond",
        "",
        *[f"- {name}: {url} ({error})" for name, url, error in unreachable],
        "",
        "## Merged duplicates (rows per company; first name kept, other names become aliases)",
        "",
        *[f"- `{key}`: " + "; ".join(names) for key, names in report["merged"].items()],
        "",
    ]
    return "\n".join(lines)


def write_companies(companies: list[Company], path: Path = COMPANIES_PATH) -> None:
    path.parent.mkdir(exist_ok=True)
    data = [c.model_dump() for c in companies]
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
