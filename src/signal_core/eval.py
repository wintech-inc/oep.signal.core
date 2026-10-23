"""Reference sets and evaluation (M1 plan section 7, M4 plan section 7 for roles).

review: draw a fixed sample per market, screen it, and write a review sheet.
freeze: store the reviewed labels in data/reference_labels.json (roles: data/reference_roles.json).
eval:   screen the reference set and report precision, recall, unknown rate, and cost.
"""

import csv
import json
import random
from collections import Counter
from pathlib import Path

from signal_core.classify import MODEL, cost_per_1000
from signal_core.companies import Company, clean_url, company_key
from signal_core.markets import LEAD_ROLES, ROLES, ROOT, Market
from signal_core.role import ACTIVITIES, role_cost_per_1000, role_url

REFERENCE_PATH = ROOT / "data" / "reference_labels.json"
EVAL_DIR = ROOT / "eval"
SAMPLE_SIZE = 100
SEED = 13
LABELS = ("in", "out", "skip")
SHEET_COLUMNS = ["company_id", "name", "url", "crm_hint", "verdict", "rule", "reason", "evidence_url", "label", "note"]
TARGETS = {"recall": 0.95, "precision": 0.90, "unknown_rate": 0.05, "cost_per_1000": 2.00}

ROLE_REFERENCE_PATH = ROOT / "data" / "reference_roles.json"
ROLE_LABELS = (*ROLES, "skip")
ROLE_EXTRA = 10
ROLE_SHEET_COLUMNS = ["company_id", "name", "url", "source", "previous_label", "role", "comment",
                      *[f for a in ACTIVITIES for f in (a, f"{a}_url")], "weak_evidence", "label", "note"]
ROLE_TARGETS = {"lead_recall": 0.95, "lead_precision": 0.90, "accuracy": 0.85, "cost_per_1000": 2.00}
CONTACT_TARGET = 0.90   # share of filled address and phone fields right in the spot check


def crm_hint(company: Company) -> str:
    return "; ".join(f"{t.market} / {t.role}" for t in company.crm)


def sample(companies: list[Company], market: Market, n: int = SAMPLE_SIZE, seed: int = SEED) -> list[Company]:
    """Half from companies the CRM tags with this market, half from the rest.

    The brief's examples_in are left out: they appear in the prompt, so they would test nothing.
    """
    examples = {company_key(clean_url(e.url) or e.url) for e in market.examples_in}
    pool = sorted((c for c in companies if c.id not in examples), key=lambda c: c.id)
    tagged = [c for c in pool if any(t.market == market.crm_market for t in c.crm)]
    tagged_ids = {c.id for c in tagged}
    rest = [c for c in pool if c.id not in tagged_ids]
    rng = random.Random(seed)
    k = min(n // 2, len(tagged))
    return rng.sample(tagged, k) + rng.sample(rest, n - k)


def sheet_path(market_id: str) -> Path:
    return EVAL_DIR / f"review_{market_id}.csv"


def write_sheet(path: Path, results: list[dict], companies: dict[str, Company]) -> None:
    path.parent.mkdir(exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=SHEET_COLUMNS, extrasaction="ignore")
        writer.writeheader()
        for r in results:
            writer.writerow({**r, "crm_hint": crm_hint(companies[r["company_id"]]), "label": "", "note": ""})


def load_labels(reference_path: Path = REFERENCE_PATH) -> list[dict]:
    return json.loads(reference_path.read_text()) if reference_path.exists() else []


def freeze(market_id: str, path: Path, allowed: tuple = LABELS, reference_path: Path = REFERENCE_PATH) -> int:
    """Read a reviewed sheet into the reference file, replacing that market's labels. Labels match the allowed
    values in any letter case."""
    with open(path, newline="", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    canonical = {a.lower(): a for a in allowed}
    missing = [r["name"] for r in rows if r["label"].strip().lower() not in canonical]
    if missing:
        raise SystemExit(f"{len(missing)} rows have no label (use {', '.join(allowed)}): {', '.join(missing[:10])}")
    new = [
        {"company_id": r["company_id"], "market_id": market_id, "label": canonical[r["label"].strip().lower()],
         "note": r["note"].strip()}
        for r in rows
        if r["label"].strip().lower() != "skip"
    ]
    kept = [l for l in load_labels(reference_path) if l["market_id"] != market_id]
    reference_path.write_text(json.dumps(kept + new, indent=2, ensure_ascii=False) + "\n")
    return len(new)


def metrics(results: list[dict], labels: dict[str, str]) -> dict:
    pairs = [(labels[r["company_id"]], r["verdict"]) for r in results]
    tp = sum(1 for l, p in pairs if l == "in" and p == "in")
    fn = sum(1 for l, p in pairs if l == "in" and p != "in")
    fp = sum(1 for l, p in pairs if l == "out" and p == "in")
    return {
        "n": len(pairs),
        "recall": tp / (tp + fn) if tp + fn else None,
        "precision": tp / (tp + fp) if tp + fp else None,
        "unknown_rate": sum(1 for _, p in pairs if p == "unknown") / len(pairs) if pairs else None,
        "errors": sum(1 for _, p in pairs if p == "error"),
        "cost_per_1000": cost_per_1000([r for r in results if r["verdict"] != "error"]),
        "confusion": Counter(pairs),
    }


def report(market: Market, results: list[dict], labels: dict[str, dict]) -> str:
    m = metrics(results, {k: v["label"] for k, v in labels.items()})

    def pct(x):
        return "n/a" if x is None else f"{x:.0%}"

    def status(key):
        x, target = m[key], TARGETS[key]
        if x is None:
            return "n/a"
        ok = x <= target if key in ("unknown_rate", "cost_per_1000") else x >= target
        return "met" if ok else "**missed**"

    verdicts = ["in", "out", "unknown", "error"]
    lines = [
        f"# Eval: {market.name} (`{market.id}`)",
        "",
        f"Reference set: {m['n']} companies reviewed by Tim. Model: `{MODEL}`.",
        "",
        "| Measure | Result | Target | |",
        "|---|---|---|---|",
        f"| Recall | {pct(m['recall'])} | ≥ {TARGETS['recall']:.0%} | {status('recall')} |",
        f"| Precision | {pct(m['precision'])} | ≥ {TARGETS['precision']:.0%} | {status('precision')} |",
        f"| Unknown | {pct(m['unknown_rate'])} | ≤ {TARGETS['unknown_rate']:.0%} | {status('unknown_rate')} |",
        f"| Cost per 1,000 | ${m['cost_per_1000']:.2f} | < ${TARGETS['cost_per_1000']:.2f} | {status('cost_per_1000')} |",
        "",
        f"Errors (API or search failures): {m['errors']}",
        "",
        "## Confusion matrix (rows: reference label, columns: verdict)",
        "",
        "| | " + " | ".join(verdicts) + " |",
        "|---|" + "---|" * len(verdicts),
        *[f"| **{l}** | " + " | ".join(str(m["confusion"][(l, v)]) for v in verdicts) + " |" for l in ("in", "out")],
        "",
        "## Disagreements",
        "",
    ]
    wrong = [r for r in results if r["verdict"] != labels[r["company_id"]]["label"]]
    for r in sorted(wrong, key=lambda r: (labels[r["company_id"]]["label"], r["name"])):
        note = labels[r["company_id"]]["note"]
        lines += [
            f"- **{r['name']}** ({r['url']}): label `{labels[r['company_id']]['label']}`, verdict `{r['verdict']}`."
            + (f" Reviewer note: {note}" if note else ""),
            f"  - {r['reason']}" + (f" Evidence: {r['evidence_url']}" if r.get("evidence_url") else ""),
        ]
    if not wrong:
        lines.append("None.")
    return "\n".join(lines) + "\n"


# Roles (stage 2)


def role_sheet_path(market_id: str) -> Path:
    return EVAL_DIR / f"review_roles_{market_id}.csv"


def role_extras(candidates: list[dict], market: Market, exclude: set[str], have: Counter,
                n: int = ROLE_EXTRA, seed: int = SEED) -> list[dict]:
    """Discovered in-market companies to test each role's precision: for every role the reference set has fewer
    than n of (by stage 2's answer), companies stage 2 gives that role, up to n in all. Never the brief's examples."""
    examples = {company_key(clean_url(e.url) or e.url) for e in market.examples_in}
    rng = random.Random(seed)
    rows = []
    for role in ROLES:
        pool = sorted((c for c in candidates if c.get("role") == role and c["company_id"] not in exclude | examples),
                      key=lambda c: c["company_id"])
        rows += rng.sample(pool, min(max(n - have[role], 0), len(pool)))
    return rows


def write_role_sheet(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=ROLE_SHEET_COLUMNS, extrasaction="ignore")
        writer.writeheader()
        for r in rows:
            writer.writerow({**r, "label": "", "note": ""})


def role_metrics(results: list[dict], labels: dict[str, str]) -> dict:
    """Lead recall and precision (any lead role counts as a lead), exact role accuracy, and the confusion matrix."""
    ran = [r for r in results if r["role"] != "error"]
    pairs = [(labels[r["company_id"]], r["role"]) for r in ran]
    tp = sum(1 for l, p in pairs if l in LEAD_ROLES and p in LEAD_ROLES)
    fn = sum(1 for l, p in pairs if l in LEAD_ROLES and p not in LEAD_ROLES)
    fp = sum(1 for l, p in pairs if l not in LEAD_ROLES and p in LEAD_ROLES)
    return {
        "n": len(results),
        "lead_recall": tp / (tp + fn) if tp + fn else None,
        "lead_precision": tp / (tp + fp) if tp + fp else None,
        "accuracy": sum(1 for l, p in pairs if l == p) / len(pairs) if pairs else None,
        "errors": len(results) - len(ran),
        "weak": [r for r in ran if r.get("weak_evidence")],
        "cost_per_1000": role_cost_per_1000(ran),
        "confusion": Counter(pairs),
    }


def role_report(market: Market, results: list[dict], labels: dict[str, dict]) -> str:
    m = role_metrics(results, {k: v["label"] for k, v in labels.items()})

    def pct(x):
        return "n/a" if x is None else f"{x:.0%}"

    def row(key, name):
        x, target = m[key], ROLE_TARGETS[key]
        if key == "cost_per_1000":
            return f"| {name} | ${x:.2f} | < ${target:.2f} | {'met' if x < target else '**missed**'} |"
        status = "n/a" if x is None else "met" if x >= target else "**missed**"
        return f"| {name} | {pct(x)} | ≥ {target:.0%} | {status} |"

    counts = Counter(v["label"] for v in labels.values())
    short = {r: "".join(w[0] for w in r.split()) for r in ROLES}   # column heads: M, CM, CR, R, SR, A
    lines = [
        f"# Role eval: {market.name} (`{market.id}`)",
        "",
        f"Reference set: {m['n']} companies in the market, roles reviewed by Tim "
        f"({', '.join(f'{counts[r]} {r}' for r in ROLES)}). Model: `{MODEL}`. "
        f"Lead roles: {', '.join(LEAD_ROLES)}.",
        "",
        "| Measure | Result | Target | |",
        "|---|---|---|---|",
        row("lead_recall", "Lead recall"),
        row("lead_precision", "Lead precision"),
        row("accuracy", "Exact role accuracy"),
        row("cost_per_1000", "Cost per 1,000"),
        "",
        f"Errors (API or search failures): {m['errors']}. "
        f"Yes answers without an evidence URL from the evidence: {len(m['weak'])}.",
        "",
        "## Confusion matrix (rows: reference label, columns: role)",
        "",
        " ".join(f"{short[r]} = {r}." for r in ROLES),
        "",
        "| | " + " | ".join(short[r] for r in ROLES) + " |",
        "|---|" + "---|" * len(ROLES),
        *[f"| **{l}** | " + " | ".join(str(m["confusion"][(l, p)]) for p in ROLES) + " |" for l in ROLES],
        "",
        "## Disagreements",
        "",
    ]

    def detail(r):
        yes = [a.replace("_", " ") for a in ACTIVITIES if r.get(a)]
        url = role_url(r)
        return (f"  - {r['comment']} Activities: {', '.join(yes) or 'none'}." + (f" Evidence: {url}" if url else ""))

    wrong = [r for r in results if r["role"] != labels[r["company_id"]]["label"]]
    order = {r: i for i, r in enumerate(ROLES)}
    for r in sorted(wrong, key=lambda r: (order.get(labels[r["company_id"]]["label"], len(order)), r["name"])):
        note = labels[r["company_id"]]["note"]
        lines += [f"- **{r.get('company_name') or r['name']}** ({r['url']}): label `{labels[r['company_id']]['label']}`, "
                  f"role `{r['role']}`." + (f" Reviewer note: {note}" if note else ""), detail(r)]
    if not wrong:
        lines.append("None.")
    lines += ["", "## Yes answers without an evidence URL from the evidence", ""]
    lines += [f"- **{r['name']}** ({r['url']}): {r['weak_evidence']}." for r in m["weak"]] or ["None."]
    return "\n".join(lines) + "\n"


def contact_report(market: Market, path: Path) -> str:
    """The contact spot check: of the filled address and phone fields Tim checked, the share that is right."""
    with open(path, newline="", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    lines = [f"# Contact spot check: {market.name} (`{market.id}`)", "",
             f"{len(rows)} exported rows checked against their map listing and website.", "",
             "| Field | Right | Checked | Share | Target |", "|---|---|---|---|---|"]
    for field, filled in (("address", ("Street address", "City")), ("phone", ("Phone",))):
        checked = [r for r in rows if any(r[c] for c in filled) and r[f"{field}_right"].strip().lower() in ("yes", "no")]
        right = sum(1 for r in checked if r[f"{field}_right"].strip().lower() == "yes")
        share = right / len(checked) if checked else None
        status = "n/a" if share is None else "met" if share >= CONTACT_TARGET else "**missed**"
        lines.append(f"| {field} | {right} | {len(checked)} | {'n/a' if share is None else f'{share:.0%}'} | "
                     f"≥ {CONTACT_TARGET:.0%}: {status} |")
    wrong = [r for r in rows if "no" in (r["address_right"].strip().lower(), r["phone_right"].strip().lower())]
    lines += ["", "## Wrong", ""]
    lines += [f"- **{r['Company']}** ({r['Homepage']}): {r['note'] or 'no note'}. Listing: {r['maps_url'] or 'none'}"
              for r in wrong] or ["None."]
    return "\n".join(lines) + "\n"


# Discovery spot check (M3 plan section 7)

DISCOVERY_REFERENCE_PATH = ROOT / "data" / "reference_discovery.json"
DISCOVERY_SAMPLE = 25
DISCOVERY_SHEET_COLUMNS = ["company_id", "name", "url", "location", "sample", "verdict", "rule", "reason",
                           "evidence_url", "found_by", "label", "note"]
DISCOVERY_TARGET = 0.90


def discovery_sheet_path(market_id: str) -> Path:
    return EVAL_DIR / f"review_discovery_{market_id}.csv"


def discovery_sample(candidates: dict[str, dict], n: int = DISCOVERY_SAMPLE, seed: int = SEED) -> list[dict]:
    """n discovered companies (not on the seed list) M1 called in, and n it called out or unknown."""
    found = sorted((c for c in candidates.values() if not c["seed"]), key=lambda c: c["company_id"])
    rng = random.Random(seed)
    rows = []
    for name, verdicts in (("in", ("in",)), ("out", ("out", "unknown"))):
        pool = [c for c in found if c.get("verdict") in verdicts]
        rows += [{**c, "sample": name} for c in rng.sample(pool, min(n, len(pool)))]
    return rows


def write_discovery_sheet(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=DISCOVERY_SHEET_COLUMNS, extrasaction="ignore")
        writer.writeheader()
        for r in rows:
            writer.writerow({**r, "found_by": "; ".join(x["detail"] for x in r["found_by"][:3]), "label": "", "note": ""})


def discovery_report(market: Market, candidates: dict[str, dict], labels: dict[str, dict]) -> str:
    """Precision of M1's in verdicts on discovered companies, and the companies it missed in the out sample."""
    rows = [(candidates[k], l) for k, l in labels.items() if k in candidates]
    said_in = [(c, l) for c, l in rows if c.get("verdict") == "in"]
    said_out = [(c, l) for c, l in rows if c.get("verdict") != "in"]
    right = sum(1 for _, l in said_in if l["label"] == "in")
    precision = right / len(said_in) if said_in else None
    missed = [(c, l) for c, l in said_out if l["label"] == "in"]
    lines = [
        f"# Discovery spot check: {market.name} (`{market.id}`)", "",
        f"Tim reviewed {len(rows)} discovered companies (not on the seed list): {len(said_in)} M1 called in, "
        f"{len(said_out)} it called out or unknown.", "",
        "| Measure | Result | Target | |", "|---|---|---|---|",
        f"| `in` verdicts right | {right} of {len(said_in)}" + (f" ({precision:.0%})" if precision is not None else "")
        + f" | ≥ {DISCOVERY_TARGET:.0%} | " + ("n/a" if precision is None else "met" if precision >= DISCOVERY_TARGET else "**missed**") + " |",
        f"| In-market companies in the out sample | {len(missed)} of {len(said_out)} | reported | |", "",
        "## Wrong `in` verdicts", "",
    ]
    wrong = [(c, l) for c, l in said_in if l["label"] != "in"]
    lines += [f"- **{c['name']}** ({c['url']}): {c['reason']}" + (f" Reviewer note: {l['note']}" if l["note"] else "")
              for c, l in wrong] or ["None."]
    lines += ["", "## In-market companies M1 called out or unknown", ""]
    lines += [f"- **{c['name']}** ({c['url']}), verdict `{c.get('verdict')}`: {c['reason']}"
              + (f" Reviewer note: {l['note']}" if l["note"] else "") for c, l in missed] or ["None."]
    return "\n".join(lines) + "\n"
