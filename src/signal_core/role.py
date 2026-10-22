"""Role classification (stage 2, M4): for a company already in a market, which of five activities does it do
there, and so which role does it have? One Claude Haiku call per company and market, over the stage-1
evidence (cached) plus one search for products like ours. The role follows from the activities in code,
by the fixed precedence in markets.ROLES.
"""

import asyncio
import hashlib
import sys
from functools import cache

import anthropic
import httpx
from pydantic import BaseModel

from signal_core.classify import EFFORT, MODEL, PRICE_IN, PRICE_OUT, PRICE_SEARCH, Classifier, _bullets, evidence_text
from signal_core.companies import Company
from signal_core.markets import ROOT, Market, load_market

PROMPT_PATH = ROOT / "prompts" / "classify_role.md"
# Each activity and the role it gives, in precedence order. A company with none of them is Adjacent.
ACTIVITIES = {
    "makes_end_product": "Manufacturer",
    "makes_component": "Component Manufacturer",
    "resells_component": "Component Reseller",
    "resells_supplies": "Supply Reseller",
    "resells_end_product": "Reseller",
}
ROLE_FIELDS = ["role", "company_name", "comment",
               *[f for a in ACTIVITIES for f in (a, f"{a}_url")], "weak_evidence", "role_version"]


class Activity(BaseModel):
    yes: bool
    evidence_url: str | None


class RoleAnswer(BaseModel):
    name: str
    makes_end_product: Activity
    makes_component: Activity
    resells_component: Activity
    resells_supplies: Activity
    resells_end_product: Activity
    comment: str


def derive_role(flags: dict) -> str:
    """The first role whose activity is yes, in precedence order; Adjacent if none."""
    return next((role for activity, role in ACTIVITIES.items() if flags.get(activity)), "Adjacent")


def role_url(result: dict) -> str | None:
    """The evidence URL of the activity that gave the company its role (stage 1's for Adjacent)."""
    activity = next((a for a, role in ACTIVITIES.items() if role == result.get("role")), None)
    return result.get(f"{activity}_url") if activity else result.get("evidence_url")


@cache
def role_prompt(market_id: str) -> str:
    market = load_market(market_id)
    return PROMPT_PATH.read_text().format(
        supplier=market.supplier,
        end_product=market.end_product,
        our_products=market.our_products,
        our_terms=", ".join(market.our_products.terms),
        role_notes=_bullets(market.role_notes),
        examples=_bullets([f"{e.name} ({e.url}): {e.role}" for e in market.examples_in if e.role]),
    )


def role_version(market_id: str) -> str:
    """Short hash of the stage-2 prompt as rendered for a market: a stored role from another version is stale."""
    return hashlib.sha1(role_prompt(market_id).encode()).hexdigest()[:12]


def role_evidence_text(company: Company, evidence: dict, products: dict) -> str:
    lines = [evidence_text(company, evidence), "", f"## Search results for products like ours: {products['query']}", ""]
    for i, r in enumerate(products["results"], 1):
        lines += [f"{i}. {r['title']} ({r['link']})", f"   {r['snippet']}"]
    if not products["results"]:
        lines.append("(no results)")
    return "\n".join(lines)


def _norm(url: str | None) -> str:
    return (url or "").split("://")[-1].removeprefix("www.").rstrip("/").lower()


def evidence_urls(evidence: dict, products: dict) -> set[str]:
    page = evidence["homepage"]
    links = [page["url"], page.get("final_url")]
    links += [r["link"] for r in evidence["search"]["results"] + products["results"]]
    return {_norm(u) for u in links if u}


class RoleClassifier(Classifier):
    """Stage 1 (the M1 classifier, unchanged) plus stage 2."""

    async def role(self, company: Company, market: Market) -> dict:
        """Stage 2 only: the role of a company assumed to be in the market."""
        result = {"company_id": company.id, "name": company.name, "url": company.url, "market_id": market.id}
        try:
            evidence, products = await asyncio.gather(
                self.fetcher.evidence(company, market), self.fetcher.product_search(company, market))
            async with self.limit:
                response = await self.llm.messages.parse(
                    model=MODEL,
                    max_tokens=4000,
                    system=role_prompt(market.id),
                    messages=[{"role": "user", "content": role_evidence_text(company, evidence, products)}],
                    output_config={"effort": EFFORT},
                    output_format=RoleAnswer,
                )
            if response.parsed_output is None:
                raise RuntimeError(f"no answer (stop_reason={response.stop_reason})")
            answer = response.parsed_output
            # A yes whose URL isn't in the evidence is a weak answer: kept, but flagged for the eval.
            urls = evidence_urls(evidence, products)
            fields = {}
            for activity in ACTIVITIES:
                a = getattr(answer, activity)
                fields |= {activity: a.yes, f"{activity}_url": a.evidence_url if a.yes else None}
            weak = [a for a in ACTIVITIES if fields[a] and _norm(fields[f"{a}_url"]) not in urls]
            return {**result, "role": derive_role(fields), "company_name": answer.name.strip() or company.name,
                    "comment": answer.comment, **fields, "weak_evidence": ", ".join(weak),
                    "role_version": role_version(market.id),
                    "role_input_tokens": response.usage.input_tokens, "role_output_tokens": response.usage.output_tokens}
        except (anthropic.APIError, httpx.HTTPError, RuntimeError, OSError) as e:
            return {**result, "role": "error", "comment": f"{type(e).__name__}: {e}"[:300]}

    async def two_stage(self, company: Company, market: Market) -> dict:
        """Stage 1; if the company is in, stage 2. Role fields are empty for companies not in."""
        stage1 = await self.classify(company, market)
        if stage1["verdict"] != "in":
            return {**stage1, **dict.fromkeys(ROLE_FIELDS)}
        return {**stage1, **await self.role(company, market)}

    async def run_many(self, step, companies: list[Company], market: Market) -> list[dict]:
        """Run self.role or self.two_stage over many companies, with a progress line."""
        done = 0

        async def one(company):
            nonlocal done
            r = await step(company, market)
            done += 1
            print(f"\r{market.id}: {done}/{len(companies)}", end="", file=sys.stderr, flush=True)
            return r

        results = await asyncio.gather(*(one(c) for c in companies))
        print(file=sys.stderr)
        return results


def role_cost_per_1000(results: list[dict]) -> float:
    """Estimated USD per 1,000 stage-2 classifications: LLM tokens plus the product search (cache ignored)."""
    ran = [r for r in results if r.get("role") not in (None, "error")]
    if not ran:
        return 0.0
    llm = sum(r["role_input_tokens"] * PRICE_IN + r["role_output_tokens"] * PRICE_OUT for r in ran) / 1e6
    return 1000 * (llm / len(ran) + PRICE_SEARCH)
