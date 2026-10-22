"""Market briefs: load and validate markets/<id>.json.

The Pydantic model here is the source of markets/schema.json
(`signal schema` regenerates it, and a test checks they match).
"""

import json
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

ROOT = Path(__file__).resolve().parents[2]
MARKETS_DIR = ROOT / "markets"
SCHEMA_PATH = MARKETS_DIR / "schema.json"


class Strict(BaseModel):
    model_config = ConfigDict(extra="forbid")


class EndProduct(Strict):
    name: str = Field(description="Singular name of the end product, e.g. 'commercial poultry house'.")
    description: str
    terms: list[str] = Field(min_length=1, description="Search terms for the end product.")
    not_included: list[str] = Field(default_factory=list)


class OurProducts(Strict):
    summary: str = Field(description="What the supplier makes for this end product.")
    category: str = Field(description="Product category for rule C, e.g. 'doors or windows'.")
    terms: list[str] = Field(default_factory=list, description="Search terms for products like ours.")


class Example(Strict):
    name: str
    url: str
    rule: str = Field(description="Rule(s) that make it IN: A, B, C, or a combination.")
    role: Literal["customer", "competitor", "both"] | None = Field(
        default=None, description="Its role to the supplier, shown as an example to the role classifier (M2).")


class PacProduct(Strict):
    name: str
    description: str
    url: str | None


class Geography(Strict):
    countries: list[str] = Field(description="Hard boundary: companies must be based in these countries (ISO codes).")
    note: str
    priority_states: list[str] = Field(description="Soft: where companies are most common. Only steers searching; never a boundary.")
    search_locations: list[str] = Field(
        default_factory=list,
        description="The hard boundary within the countries: the states or provinces a company must be based in. "
                    "Discovery searches each one; companies known to be based elsewhere are out without classifying. "
                    "Priority states only steer searching and are never a boundary.")


class Market(Strict):
    id: str = Field(pattern=r"^[a-z0-9_]+$")
    name: str
    supplier: str
    crm_market: str | None = Field(default=None, description="The CRM's market name for this brief (eval only).")
    end_product: EndProduct
    our_products: OurProducts
    notes: list[str] = Field(default_factory=list)
    role_notes: list[str] = Field(
        default_factory=list, description="Market-specific clarifications for the role classifier (M2), one sentence each.")
    examples_in: list[Example] = Field(default_factory=list)
    pac_products: list[PacProduct] = Field(default_factory=list)
    geography: Geography | None = None


def schema() -> dict:
    return {"$schema": "https://json-schema.org/draft/2020-12/schema", **Market.model_json_schema()}


def write_schema() -> Path:
    SCHEMA_PATH.write_text(json.dumps(schema(), indent=2) + "\n")
    return SCHEMA_PATH


def market_ids() -> list[str]:
    return sorted(p.stem for p in MARKETS_DIR.glob("*.json") if p.name != "schema.json" and "." not in p.stem)


def load_market(market_id: str) -> Market:
    path = MARKETS_DIR / f"{market_id}.json"
    if not path.exists():
        raise SystemExit(f"Unknown market '{market_id}'. Available: {', '.join(market_ids())}")
    market = Market.model_validate_json(path.read_text())
    if market.id != market_id:
        raise ValueError(f"{path.name}: id '{market.id}' does not match the file name")
    return market
