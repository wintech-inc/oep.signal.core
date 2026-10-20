"""Reference set and evaluation (plan section 7).

review: draw a fixed sample per market, screen it, and write a review sheet.
freeze: store the reviewed labels in data/reference_labels.json.
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

REFERENCE_PATH = ROOT / "data" / "reference_labels.json"
EVAL_DIR = ROOT / "eval"
SAMPLE_SIZE = 100
SEED = 13
LABELS = ("in", "out", "skip")
SHEET_COLUMNS = ["company_id", "name", "url", "crm_hint", "verdict", "rule", "reason", "evidence_url", "label", "note"]
TARGETS = {"recall": 0.95, "precision": 0.90, "unknown_rate": 0.05, "cost_per_1000": 2.00}


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


def load_labels() -> list[dict]:
    return json.loads(REFERENCE_PATH.read_text()) if REFERENCE_PATH.exists() else []


def freeze(market_id: str, path: Path) -> int:
    """Read a reviewed sheet into data/reference_labels.json, replacing that market's labels."""
    with open(path, newline="", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    missing = [r["name"] for r in rows if r["label"].strip().lower() not in LABELS]
    if missing:
        raise SystemExit(f"{len(missing)} rows have no label (use {', '.join(LABELS)}): {', '.join(missing[:10])}")
    new = [
        {"company_id": r["company_id"], "market_id": market_id, "label": r["label"].strip().lower(), "note": r["note"].strip()}
        for r in rows
        if r["label"].strip().lower() != "skip"
    ]
    labels = [l for l in load_labels() if l["market_id"] != market_id] + new
    REFERENCE_PATH.write_text(json.dumps(labels, indent=2, ensure_ascii=False) + "\n")
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
