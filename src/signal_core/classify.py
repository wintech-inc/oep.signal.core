"""Market screening: one Claude Haiku call per company and market, over cached evidence."""

import asyncio
import sys
from functools import cache
from typing import Literal

import anthropic
import httpx
from pydantic import BaseModel

from signal_core.companies import Company
from signal_core.evidence import Fetcher
from signal_core.markets import ROOT, Market, load_market

PROMPT_PATH = ROOT / "prompts" / "screen_market.md"
MODEL = "claude-haiku-5-5"
EFFORT = "low"
# USD per million tokens (Haiku 5.5, prompts under 100K tokens) and per Serper query.
PRICE_IN, PRICE_OUT, PRICE_SEARCH = 0.10, 0.50, 0.001


class Verdict(BaseModel):
    reason: str
    verdict: Literal["in", "out", "unknown"]
    rule: Literal["A", "B", "C"] | None
    evidence_url: str | None


def _bullets(items: list[str]) -> str:
    return "\n".join(f"- {item}" for item in items) or "- (none)"


@cache
def system_prompt(market_id: str) -> str:
    market = load_market(market_id)
    return PROMPT_PATH.read_text().format(
        supplier=market.supplier,
        end_product=market.end_product,
        our_products=market.our_products,
        not_included=_bullets(market.end_product.not_included),
        our_terms=", ".join(market.our_products.terms),
        notes=_bullets(market.notes),
        geography=market.geography.note if market.geography else "Anywhere.",
        examples=_bullets([f"{e.name} ({e.url}): IN under rule {e.rule}" for e in market.examples_in]),
    )


def evidence_text(company: Company, evidence: dict) -> str:
    page, search = evidence["homepage"], evidence["search"]
    names = company.name + (f" (also known as: {'; '.join(company.aliases)})" if company.aliases else "")
    lines = [f"Company: {names}", f"URL: {company.url}", ""]
    if page["text"]:
        lines += [f"## Homepage ({page['final_url']})", "", page["text"], ""]
    else:
        lines += ["## Homepage", "", f"(no text: {page['error'] or 'HTTP ' + str(page['status'])})", ""]
    lines += [f"## Search results for: {search['query']}", ""]
    for i, r in enumerate(search["results"], 1):
        lines += [f"{i}. {r['title']} ({r['link']})", f"   {r['snippet']}"]
    if not search["results"]:
        lines.append("(no results)")
    return "\n".join(lines)


class Classifier:
    def __init__(self, concurrency: int = 16):
        self.fetcher = Fetcher(concurrency)
        self.llm = anthropic.AsyncAnthropic(max_retries=4)
        self.limit = asyncio.Semaphore(concurrency)

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc):
        await self.fetcher.__aexit__(*exc)
        await self.llm.close()

    async def classify(self, company: Company, market: Market) -> dict:
        result = {"company_id": company.id, "name": company.name, "url": company.url, "market_id": market.id}
        try:
            evidence = await self.fetcher.evidence(company, market)
            if not evidence["homepage"]["text"] and not evidence["search"]["results"]:
                verdict = Verdict(reason="No usable evidence: no homepage text and no search results.",
                                  verdict="unknown", rule=None, evidence_url=None)
                return {**result, **verdict.model_dump(), "input_tokens": 0, "output_tokens": 0}
            async with self.limit:
                response = await self.llm.messages.parse(
                    model=MODEL,
                    max_tokens=4000,
                    system=system_prompt(market.id),
                    messages=[{"role": "user", "content": evidence_text(company, evidence)}],
                    output_config={"effort": EFFORT},
                    output_format=Verdict,
                )
            if response.parsed_output is None:
                raise RuntimeError(f"no verdict (stop_reason={response.stop_reason})")
            verdict = response.parsed_output
            if verdict.verdict != "in":
                verdict.rule = None
            return {**result, **verdict.model_dump(),
                    "input_tokens": response.usage.input_tokens, "output_tokens": response.usage.output_tokens}
        except (anthropic.APIError, httpx.HTTPError, RuntimeError, OSError) as e:
            return {**result, "verdict": "error", "reason": f"{type(e).__name__}: {e}"[:300]}

    async def classify_many(self, companies: list[Company], market: Market) -> list[dict]:
        done = 0

        async def one(company):
            nonlocal done
            r = await self.classify(company, market)
            done += 1
            print(f"\r{market.id}: {done}/{len(companies)}", end="", file=sys.stderr, flush=True)
            return r

        results = await asyncio.gather(*(one(c) for c in companies))
        print(file=sys.stderr)
        return results


def cost_per_1000(results: list[dict]) -> float:
    """Estimated USD per 1,000 classifications: LLM tokens used plus one search each (cache ignored)."""
    if not results:
        return 0.0
    tokens_in = sum(r.get("input_tokens", 0) for r in results)
    tokens_out = sum(r.get("output_tokens", 0) for r in results)
    llm = (tokens_in * PRICE_IN + tokens_out * PRICE_OUT) / 1e6
    return 1000 * (llm / len(results) + PRICE_SEARCH)
