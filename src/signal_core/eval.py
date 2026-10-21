"""Reference sets and evaluation (M1 plan section 7, M2 plan section 6).

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
from signal_core.markets import ROOT, Market
from signal_core.role import role_cost_per_1000

REFERENCE_PATH = ROOT / "data" / "reference_labels.json"
EVAL_DIR = ROOT / "eval"
SAMPLE_SIZE = 100
SEED = 13
LABELS = ("in", "out", "skip")
SHEET_COLUMNS = ["company_id", "name", "url", "crm_hint", "verdict", "rule", "reason", "evidence_url", "label", "note"]
TARGETS = {"recall": 0.95, "precision": 0.90, "unknown_rate": 0.05, "cost_per_1000": 2.00}

ROLE_REFERENCE_PATH = ROOT / "data" / "reference_roles.json"
ROLES = ("customer", "competitor", "both", "neither")
ROLE_LABELS = (*ROLES, "skip")
ROLE_EXTRA = 25
ROLE_SHEET_COLUMNS = ["company_id", "name", "url", "source", "verdict", "reason", "role", "role_reason",
                      "customer_evidence_url", "competitor_evidence_url", "weak_evidence", "label", "note"]
ROLE_TARGETS = {"customer_recall": 0.95, "customer_precision": 0.90,
                "competitor_recall": 0.85, "competitor_precision": 0.85, "cost_per_1000": 2.00}


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
    """Read a reviewed sheet into the reference file, replacing that market's labels."""
    with open(path, newline="", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    missing = [r["name"] for r in rows if r["label"].strip().lower() not in allowed]
    if missing:
        raise SystemExit(f"{len(missing)} rows have no label (use {', '.join(allowed)}): {', '.join(missing[:10])}")
    new = [
        {"company_id": r["company_id"], "market_id": market_id, "label": r["label"].strip().lower(), "note": r["note"].strip()}
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


def role_extras(results: list[dict], market: Market, exclude: set[str], n: int = ROLE_EXTRA, seed: int = SEED) -> list[dict]:
    """Up to n screened companies that stage 2 calls competitor or both, outside the reference set and examples.

    The CRM list is mostly customers and leads; these add competitors to test competitor precision.
    """
    examples = {company_key(clean_url(e.url) or e.url) for e in market.examples_in}
    pool = sorted((r for r in results if r.get("role") in ("competitor", "both")
                   and r["company_id"] not in exclude | examples), key=lambda r: r["company_id"])
    return random.Random(seed).sample(pool, min(n, len(pool)))


def write_role_sheet(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=ROLE_SHEET_COLUMNS, extrasaction="ignore")
        writer.writeheader()
        for r in rows:
            writer.writerow({**r, "label": "", "note": ""})


def role_metrics(results: list[dict], labels: dict[str, str]) -> dict:
    """Customer and competitor recall and precision ('both' counts as yes for each), exact accuracy, confusion."""
    ran = [r for r in results if r["role"] != "error"]
    pairs = [(labels[r["company_id"]], r["role"]) for r in ran]

    def recall_precision(yes: tuple) -> tuple:
        tp = sum(1 for l, p in pairs if l in yes and p in yes)
        fn = sum(1 for l, p in pairs if l in yes and p not in yes)
        fp = sum(1 for l, p in pairs if l not in yes and p in yes)
        return (tp / (tp + fn) if tp + fn else None, tp / (tp + fp) if tp + fp else None)

    customer, competitor = recall_precision(("customer", "both")), recall_precision(("competitor", "both"))
    return {
        "n": len(results),
        "customer_recall": customer[0], "customer_precision": customer[1],
        "competitor_recall": competitor[0], "competitor_precision": competitor[1],
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
    lines = [
        f"# Role eval: {market.name} (`{market.id}`)",
        "",
        f"Reference set: {m['n']} companies in the market, roles reviewed by Tim "
        f"({', '.join(f'{counts[r]} {r}' for r in ROLES)}). Model: `{MODEL}`.",
        "",
        "| Measure | Result | Target | |",
        "|---|---|---|---|",
        row("customer_recall", "Customer recall"),
        row("customer_precision", "Customer precision"),
        row("competitor_recall", "Competitor recall"),
        row("competitor_precision", "Competitor precision"),
        row("cost_per_1000", "Cost per 1,000"),
        "",
        f"Exact role accuracy: {pct(m['accuracy'])}. Errors (API or search failures): {m['errors']}. "
        f"Yes answers without an evidence URL from the evidence: {len(m['weak'])}.",
        "",
        "## Confusion matrix (rows: reference label, columns: role)",
        "",
        "| | " + " | ".join(ROLES) + " |",
        "|---|" + "---|" * len(ROLES),
        *[f"| **{l}** | " + " | ".join(str(m["confusion"][(l, p)]) for p in ROLES) + " |" for l in ROLES],
        "",
        "## Disagreements",
        "",
    ]

    def detail(r):
        urls = [f"{k}: {r[f'{k}_evidence_url']}" for k in ("customer", "competitor") if r.get(f"{k}_evidence_url")]
        return f"  - {r['role_reason']}" + (f" Evidence: {'; '.join(urls)}" if urls else "")

    wrong = [r for r in results if r["role"] != labels[r["company_id"]]["label"]]
    for r in sorted(wrong, key=lambda r: (labels[r["company_id"]]["label"], r["name"])):
        note = labels[r["company_id"]]["note"]
        lines += [f"- **{r['name']}** ({r['url']}): label `{labels[r['company_id']]['label']}`, role `{r['role']}`."
                  + (f" Reviewer note: {note}" if note else ""), detail(r)]
    if not wrong:
        lines.append("None.")
    lines += ["", "## Yes answers without an evidence URL from the evidence", ""]
    lines += [f"- **{r['name']}** ({r['url']}): {r['weak_evidence']}." for r in m["weak"]] or ["None."]
    return "\n".join(lines) + "\n"
