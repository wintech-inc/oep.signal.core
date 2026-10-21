"""signal: command line for SIGNAL.

  signal sanitize docs/sample_pac_companies.csv
  signal classify https://ranchkingblinds.com --market pac_hunting_blinds
  signal classify --all --market pac_hunting_blinds
  signal review --market pac_poultry_houses
  signal freeze --market pac_poultry_houses
  signal eval --market pac_poultry_houses
  signal role https://www.hogslat.com --market pac_poultry_houses
  signal role --all --market pac_poultry_houses
  signal review --roles --market pac_poultry_houses pac_hunting_blinds
  signal freeze --roles --market pac_poultry_houses
  signal eval --roles --market pac_poultry_houses
  signal schema
  signal queries --market pac_hunting_blinds
  signal discover --market pac_hunting_blinds
  signal discover --market pac_hunting_blinds --no-seeds
  signal probe --market pac_hunting_blinds
  signal review --discovered --market pac_hunting_blinds
  signal freeze --discovered --market pac_hunting_blinds
  signal eval --discovered --market pac_hunting_blinds
"""

import argparse
import asyncio
import csv
import json
from pathlib import Path

from dotenv import load_dotenv

from signal_core import discover as dc
from signal_core import eval as ev
from signal_core.classify import Classifier, cost_per_1000
from signal_core.companies import (
    Company, clean_url, company_key, find_company, load_companies, sanitize, write_companies,
)
from signal_core.markets import ROOT, load_market, market_ids, write_schema
from signal_core.role import ROLE_FIELDS, RoleClassifier, role_cost_per_1000


def cmd_sanitize(args):
    companies, report = asyncio.run(sanitize(Path(args.csv), check=not args.no_check))
    write_companies(companies)
    report_path = ROOT / "data" / "pac_companies_sanitize_report.md"
    report_path.write_text(report)
    print(f"{len(companies)} companies written to data/pac_companies.json; report in {report_path.relative_to(ROOT)}")


async def _classify(companies, market):
    async with Classifier() as classifier:
        return await classifier.classify_many(companies, market)


def _companies(args) -> list[Company]:
    """Every known company with --all, else the given URLs (known companies keep their names)."""
    known = load_companies()
    if args.all:
        return known
    companies = []
    for url in args.urls:
        cleaned = clean_url(url)
        if cleaned is None:
            raise SystemExit(f"Not a usable URL: {url}")
        companies.append(find_company(known, cleaned) or Company(id=company_key(cleaned), name=company_key(cleaned), url=cleaned))
    return companies


def cmd_classify(args):
    market = load_market(args.market)
    companies = _companies(args)
    results = asyncio.run(_classify(companies, market))
    if args.all:
        path = ev.EVAL_DIR / f"screen_{market.id}.csv"
        ev.write_sheet(path, results, {c.id: c for c in companies})
        counts = {v: sum(r["verdict"] == v for r in results) for v in ("in", "out", "unknown", "error")}
        print(f"{counts}; about ${cost_per_1000(results):.2f} per 1,000. Written to {path.relative_to(ROOT)}")
    else:
        for r in results:
            print(json.dumps(r, indent=2))


async def _two_stage(companies, market):
    async with RoleClassifier() as classifier:
        return await classifier.run_many(classifier.two_stage, companies, market)


def _write_roles(market, results):
    path = ev.EVAL_DIR / f"roles_{market.id}.csv"
    columns = ["company_id", "name", "url", "verdict", "rule", "reason", "evidence_url", *ROLE_FIELDS]
    path.parent.mkdir(exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(results)
    return path


def cmd_role(args):
    market = load_market(args.market)
    results = asyncio.run(_two_stage(_companies(args), market))
    if args.all:
        path = _write_roles(market, results)
        roles = {v: sum(r["role"] == v for r in results) for v in (*ev.ROLES, "error")}
        print(f"{roles}; stage 2 about ${role_cost_per_1000(results):.2f} per 1,000. Written to {path.relative_to(ROOT)}")
    else:
        for r in results:
            print(json.dumps(r, indent=2))


async def _review_roles(companies, market, reference_ids):
    """Both stages over the whole list; stage 2 also for reference companies stage 1 didn't call in."""
    async with RoleClassifier() as classifier:
        results = await classifier.run_many(classifier.two_stage, companies, market)
        by_id = {r["company_id"]: r for r in results}
        redo = [c for c in companies if c.id in reference_ids and by_id[c.id]["role"] is None]
        for r in await classifier.run_many(classifier.role, redo, market):
            by_id[r["company_id"]] = {**by_id[r["company_id"]], **r}
    return [by_id[c.id] for c in companies]


def cmd_review_roles(args):
    companies = load_companies()
    for market_id in args.market:
        market = load_market(market_id)
        reference_ids = [l["company_id"] for l in ev.load_labels() if l["market_id"] == market.id and l["label"] == "in"]
        results = asyncio.run(_review_roles(companies, market, set(reference_ids)))
        _write_roles(market, results)
        by_id = {r["company_id"]: r for r in results}
        rows = [{**by_id[i], "source": "reference"} for i in reference_ids]
        rows += [{**r, "source": "screen"} for r in ev.role_extras(results, market, set(reference_ids))]
        path = ev.role_sheet_path(market.id)
        ev.write_role_sheet(path, rows)
        print(f"{len(rows)} rows written to {path.relative_to(ROOT)}. Fill in 'label' ({', '.join(ev.ROLE_LABELS)}), "
              f"then run: signal freeze --roles --market {market.id}")


def cmd_review(args):
    if args.roles:
        return cmd_review_roles(args)
    if args.discovered:
        for market_id in args.market:
            state = dc.load_state(market_id)
            if not state:
                raise SystemExit(f"No discovery run for {market_id}. Run: signal discover --market {market_id}")
            rows = ev.discovery_sample(state["candidates"])
            path = ev.discovery_sheet_path(market_id)
            ev.write_discovery_sheet(path, rows)
            print(f"{len(rows)} rows written to {path.relative_to(ROOT)}. Fill in 'label' (in, out, or skip), "
                  f"then run: signal freeze --discovered --market {market_id}")
        return
    companies = load_companies()
    for market_id in args.market:
        market = load_market(market_id)
        chosen = ev.sample(companies, market, n=args.n)
        results = asyncio.run(_classify(chosen, market))
        path = ev.sheet_path(market.id)
        ev.write_sheet(path, results, {c.id: c for c in chosen})
        print(f"{len(results)} rows written to {path.relative_to(ROOT)}. Fill in 'label' (in, out, or skip), then run: signal freeze --market {market.id}")


def cmd_freeze(args):
    if args.discovered:
        path = Path(args.sheet) if args.sheet else ev.discovery_sheet_path(args.market)
        n = ev.freeze(args.market, path, ev.LABELS, ev.DISCOVERY_REFERENCE_PATH)
        print(f"{n} spot-check labels for {args.market} stored in {ev.DISCOVERY_REFERENCE_PATH.relative_to(ROOT)}")
        return
    if args.roles:
        path = Path(args.sheet) if args.sheet else ev.role_sheet_path(args.market)
        n = ev.freeze(args.market, path, ev.ROLE_LABELS, ev.ROLE_REFERENCE_PATH)
        print(f"{n} role labels for {args.market} stored in {ev.ROLE_REFERENCE_PATH.relative_to(ROOT)}")
        return
    path = Path(args.sheet) if args.sheet else ev.sheet_path(args.market)
    n = ev.freeze(args.market, path)
    print(f"{n} reference labels for {args.market} stored in {ev.REFERENCE_PATH.relative_to(ROOT)}")


async def _roles(companies, market):
    async with RoleClassifier() as classifier:
        return await classifier.run_many(classifier.role, companies, market)


def cmd_eval_roles(args):
    """Stage 2 alone on the role reference set, so stage-1 noise doesn't blur the result."""
    market = load_market(args.market)
    labels = {l["company_id"]: l for l in ev.load_labels(ev.ROLE_REFERENCE_PATH) if l["market_id"] == market.id}
    if not labels:
        raise SystemExit(f"No role labels for {market.id}. Run: signal review --roles --market {market.id}, then signal freeze --roles")
    by_id = {c.id: c for c in load_companies()}
    results = asyncio.run(_roles([by_id[i] for i in labels], market))
    text = ev.role_report(market, results, labels)
    path = ev.EVAL_DIR / f"results_roles_{market.id}.md"
    path.write_text(text)
    print(text)
    print(f"Written to {path.relative_to(ROOT)}")


def cmd_eval(args):
    if args.roles:
        return cmd_eval_roles(args)
    if args.discovered:
        return cmd_eval_discovered(args)
    market = load_market(args.market)
    labels = {l["company_id"]: l for l in ev.load_labels() if l["market_id"] == market.id}
    if not labels:
        raise SystemExit(f"No reference labels for {market.id}. Run: signal review --market {market.id}, then signal freeze")
    by_id = {c.id: c for c in load_companies()}
    missing = [i for i in labels if i not in by_id]
    if missing:
        raise SystemExit(f"Reference companies missing from data/pac_companies.json: {', '.join(missing)}")
    results = asyncio.run(_classify([by_id[i] for i in labels], market))
    text = ev.report(market, results, labels)
    path = ev.EVAL_DIR / f"results_{market.id}.md"
    path.write_text(text)
    print(text)
    print(f"Written to {path.relative_to(ROOT)}")


def cmd_eval_discovered(args):
    """Spot check of M1 on discovered companies, from the verdicts stored by the discovery run."""
    market = load_market(args.market)
    labels = {l["company_id"]: l for l in ev.load_labels(ev.DISCOVERY_REFERENCE_PATH) if l["market_id"] == market.id}
    state = dc.load_state(market.id)
    if not labels or not state:
        raise SystemExit(f"No spot-check labels or discovery run for {market.id}. Run: signal review --discovered, then signal freeze --discovered")
    text = ev.discovery_report(market, state["candidates"], labels)
    path = ev.EVAL_DIR / f"results_discovery_{market.id}.md"
    path.write_text(text)
    print(text)
    print(f"Written to {path.relative_to(ROOT)}")


def cmd_queries(args):
    market = load_market(args.market)
    path = dc.queries_path(market.id)
    if path.exists() and not args.force:
        raise SystemExit(f"{path.relative_to(ROOT)} exists; edit it, or use --force to write a new one")
    queries = asyncio.run(dc.write_queries(market))
    print(f"{path.relative_to(ROOT)} written: {len(queries.company_queries)} company, {len(queries.nearby_queries)} nearby, "
          f"{len(queries.list_queries)} list queries, {len(queries.list_terms)} list terms")


def _write_discovery_outputs(market, blind: bool) -> list[Path]:
    state = dc.load_state(market.id, blind)
    suffix = ".blind" if blind else ""
    path = ev.EVAL_DIR / f"discovery_{market.id}{suffix}.md"
    path.write_text(dc.report(market, state))
    return [path] if blind else [path, dc.write_leads(market.id, state)]


async def _discover(market, args):
    sources = set(args.sources.split(",")) if args.sources else set(dc.SOURCES)
    unknown = sources - set(dc.SOURCES)
    if unknown:
        raise SystemExit(f"Unknown sources: {', '.join(sorted(unknown))}. Sources: {', '.join(dc.SOURCES)}")
    async with dc.Discovery(market, blind=args.no_seeds, sources=sources, max_cost=args.max_cost,
                            reclassify=args.reclassify) as discovery:
        await discovery.run(args.rounds)


def cmd_discover(args):
    market = load_market(args.market)
    asyncio.run(_discover(market, args))
    paths = _write_discovery_outputs(market, args.no_seeds)
    print(f"Written: {dc.state_path(market.id, args.no_seeds).relative_to(ROOT)}, "
          + ", ".join(str(p.relative_to(ROOT)) for p in paths))


async def _probe(market, args):
    async with dc.Discovery(market, max_cost=args.max_cost) as discovery:
        return await discovery.probe(seed=args.seed)


def cmd_probe(args):
    market = load_market(args.market)
    if not dc.load_state(market.id):
        raise SystemExit(f"No discovery run for {market.id}. Run: signal discover --market {market.id}")
    result = asyncio.run(_probe(market, args))
    path = ev.EVAL_DIR / f"probe_{market.id}.md"
    text = dc.probe_report(market, result)
    path.write_text(text)
    paths = _write_discovery_outputs(market, False)
    print(text)
    print(f"Written: {path.relative_to(ROOT)}, " + ", ".join(str(p.relative_to(ROOT)) for p in paths))


def cmd_schema(args):
    path = write_schema()
    for market_id in market_ids():
        load_market(market_id)
    print(f"{path.relative_to(ROOT)} written; briefs valid: {', '.join(market_ids())}")


def main():
    load_dotenv(ROOT / ".env")
    parser = argparse.ArgumentParser(prog="signal", description="SIGNAL market screening")
    sub = parser.add_subparsers(required=True)

    p = sub.add_parser("sanitize", help="Clean the CRM export into data/pac_companies.json")
    p.add_argument("csv")
    p.add_argument("--no-check", action="store_true", help="Skip the site-responds check")
    p.set_defaults(func=cmd_sanitize)

    p = sub.add_parser("classify", help="Screen companies for one market")
    p.add_argument("urls", nargs="*")
    p.add_argument("--market", required=True)
    p.add_argument("--all", action="store_true", help="Screen every company; writes eval/screen_<market>.csv")
    p.set_defaults(func=cmd_classify)

    p = sub.add_parser("role", help="Both stages: market screen, then customer/competitor role for companies in it")
    p.add_argument("urls", nargs="*")
    p.add_argument("--market", required=True)
    p.add_argument("--all", action="store_true", help="Every company; writes eval/roles_<market>.csv")
    p.set_defaults(func=cmd_role)

    p = sub.add_parser("review", help="Sample, screen, and write eval/review_<market>.csv for review")
    p.add_argument("--market", required=True, nargs="+")
    p.add_argument("--n", type=int, default=ev.SAMPLE_SIZE)
    p.add_argument("--roles", action="store_true", help="Role reference set instead -> eval/review_roles_<market>.csv")
    p.add_argument("--discovered", action="store_true", help="Spot check of discovered companies -> eval/review_discovery_<market>.csv")
    p.set_defaults(func=cmd_review)

    p = sub.add_parser("freeze", help="Store a reviewed sheet in data/reference_labels.json")
    p.add_argument("--market", required=True)
    p.add_argument("--sheet", help="Defaults to eval/review_<market>.csv (with --roles, eval/review_roles_<market>.csv)")
    p.add_argument("--roles", action="store_true", help="Role labels -> data/reference_roles.json")
    p.add_argument("--discovered", action="store_true", help="Spot-check labels -> data/reference_discovery.json")
    p.set_defaults(func=cmd_freeze)

    p = sub.add_parser("eval", help="Measure a market against the reference set")
    p.add_argument("--market", required=True)
    p.add_argument("--roles", action="store_true", help="Measure stage 2 against data/reference_roles.json")
    p.add_argument("--discovered", action="store_true", help="Spot-check precision on discovered companies")
    p.set_defaults(func=cmd_eval)

    p = sub.add_parser("queries", help="Write the first markets/<market>.discovery.json from the brief")
    p.add_argument("--market", required=True)
    p.add_argument("--force", action="store_true", help="Overwrite an existing query file")
    p.set_defaults(func=cmd_queries)

    p = sub.add_parser("discover", help="Find companies for a market from every source and classify them")
    p.add_argument("--market", required=True)
    p.add_argument("--no-seeds", action="store_true", help="Blind run without the seed list -> data/discovery/<market>.blind.json")
    p.add_argument("--sources", help=f"Comma-separated subset of: {', '.join(dc.SOURCES)} (default: all)")
    p.add_argument("--rounds", type=int, default=dc.ROUNDS, help="Most rounds in this run")
    p.add_argument("--max-cost", type=float, default=dc.MAX_COST, help="Stop starting new work at this estimated spend (USD)")
    p.add_argument("--reclassify", action="store_true", help="Ignore stored verdicts and classify again")
    p.set_defaults(func=cmd_discover)

    p = sub.add_parser("probe", help="Fresh-eyes completeness check: new searches, share already on the list")
    p.add_argument("--market", required=True)
    p.add_argument("--max-cost", type=float, default=5.0)
    p.add_argument("--seed", type=int, help="Random seed for the states searched (default: random)")
    p.set_defaults(func=cmd_probe)

    p = sub.add_parser("schema", help="Regenerate markets/schema.json and validate every brief")
    p.set_defaults(func=cmd_schema)

    args = parser.parse_args()
    if getattr(args, "urls", None) == [] and not getattr(args, "all", True):
        parser.error("give one or more URLs, or --all")
    args.func(args)


if __name__ == "__main__":
    main()
