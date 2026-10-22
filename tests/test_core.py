import json

import pytest

from signal_core import markets
from signal_core.classify import system_prompt
from signal_core.companies import Company, clean_url, company_key, merge_rows
from collections import Counter

from signal_core.eval import ROLE_LABELS, freeze, load_labels, metrics, role_extras, role_metrics, sample
from signal_core.evidence import MAX_QUERY_WORDS, page_text, product_search_query, search_query
from signal_core.role import ACTIVITIES, derive_role, role_prompt


@pytest.mark.parametrize("raw, expected", [
    ("www.wickbuildings.com", "https://www.wickbuildings.com"),
    ("  https://a.com/x/?q=1#f ", "https://a.com/x/"),
    ("https://all-rite.com - https://all-rite.com/", "https://all-rite.com/"),
    ("N/A - https://N/A", None),
    ("No links found", None),
    ("", None),
])
def test_clean_url(raw, expected):
    assert clean_url(raw) == expected


def test_company_key():
    assert company_key("https://www.Hogslat.com/poultry") == "hogslat.com"
    assert company_key("https://www.facebook.com/KuduOutdoorProducts/") == "facebook.com/kuduoutdoorproducts"


def test_merge_rows():
    rows = [
        {"company": "Acme", "home_page": "https://www.acme.com/", "markets": "Agriculture, Poultry", "role": "Lead"},
        {"company": "Acme LLC", "home_page": "acme.com/about", "markets": "Poultry", "role": "Customer"},
        {"company": "Nolink", "home_page": "", "markets": "Poultry", "role": "Lead"},
    ]
    companies, report = merge_rows(rows)
    assert len(companies) == 1
    acme = companies[0]
    assert (acme.id, acme.name, acme.aliases) == ("acme.com", "Acme", ["Acme LLC"])
    assert [(t.market, t.role) for t in acme.crm] == [("Agriculture", "Lead"), ("Poultry", "Lead"), ("Poultry", "Customer")]
    assert report["no_url"] == ["Nolink"]
    assert report["merged"] == {"acme.com": ["Acme", "Acme LLC"]}


def test_briefs_validate_and_schema_is_current():
    assert markets.market_ids()
    for market_id in markets.market_ids():
        markets.load_market(market_id)
    assert json.loads(markets.SCHEMA_PATH.read_text()) == markets.schema(), "run: uv run signal schema"


def test_prompt_renders():
    for market_id in markets.market_ids():
        for prompt in (system_prompt(market_id), role_prompt(market_id)):
            assert "{" not in prompt and markets.load_market(market_id).end_product.name in prompt
        assert "role" not in system_prompt(market_id), "stage-1 prompt must not show stage-2 fields"


def test_search_query():
    market = markets.load_market("pac_poultry_houses")
    site = Company(id="acme.com", name="Acme", url="https://www.acme.com/x")
    query = search_query(site, market)
    assert query.startswith('site:acme.com ("poultry house" OR ')
    assert len(query.replace(" OR ", " ").split()) <= MAX_QUERY_WORDS
    social = Company(id="facebook.com/acme", name="Acme Blinds", url="https://facebook.com/acme")
    assert search_query(social, market).startswith('"Acme Blinds" (')


def test_product_search_query():
    market = markets.load_market("pac_poultry_houses")
    query = product_search_query(Company(id="acme.com", name="Acme", url="https://acme.com"), market)
    assert query.startswith('site:acme.com ("tunnel door" OR ') and '"poultry house"' not in query
    assert len(query.replace(" OR ", " ").split()) <= MAX_QUERY_WORDS


def test_derive_role_by_precedence():
    assert tuple(ACTIVITIES.values()) + ("Adjacent",) == markets.ROLES
    assert derive_role({a: True for a in ACTIVITIES}) == "Manufacturer"
    assert derive_role({"resells_end_product": True, "resells_supplies": True}) == "Supply Reseller"
    assert derive_role({"resells_end_product": True, "resells_component": True}) == "Component Reseller"
    assert derive_role({"resells_end_product": True}) == "Reseller"
    assert derive_role({a: False for a in ACTIVITIES}) == "Adjacent"


def test_page_text():
    html = "<html><head><title>T</title><meta name='description' content='D'></head><body><script>x()</script><p>Hello</p>  <p>world</p></body></html>"
    assert page_text(html) == "T | D | Hello world"


def test_sample_is_fixed_and_split():
    market = markets.load_market("pac_hunting_blinds")
    companies = [Company(id=f"c{i}.com", name=f"C{i}", url=f"https://c{i}.com",
                         crm=[{"market": "Hunting Blinds" if i % 3 == 0 else "Sheds", "role": "Lead"}]) for i in range(300)]
    chosen = sample(companies, market, n=20)
    assert [c.id for c in chosen] == [c.id for c in sample(companies, market, n=20)]
    assert sum(c.crm[0].market == "Hunting Blinds" for c in chosen) == 10


def test_metrics():
    results = [{"company_id": str(i), "verdict": v, "input_tokens": 0, "output_tokens": 0}
               for i, v in enumerate(["in", "in", "out", "unknown", "in"])]
    labels = {"0": "in", "1": "in", "2": "in", "3": "out", "4": "out"}
    m = metrics(results, labels)
    assert (m["recall"], m["precision"], m["unknown_rate"]) == (2 / 3, 2 / 3, 1 / 5)


def test_role_metrics():
    roles = ["Manufacturer", "Supply Reseller", "Reseller", "Component Manufacturer", "Adjacent"]
    labels = {"0": "Manufacturer", "1": "Component Reseller", "2": "Manufacturer", "3": "Component Manufacturer",
              "4": "Reseller"}
    results = [{"company_id": str(i), "role": r, "role_input_tokens": 0, "role_output_tokens": 0} for i, r in enumerate(roles)]
    m = role_metrics(results, labels)
    assert (m["lead_recall"], m["lead_precision"]) == (2 / 3, 1.0)
    assert m["accuracy"] == 2 / 5


def test_role_extras_top_up_rare_roles_and_skip_reference_and_examples():
    market = markets.load_market("pac_poultry_houses")
    found = [{"company_id": f"r{i}.com", "role": "Reseller"} for i in range(5)]
    found += [{"company_id": f"m{i}.com", "role": "Manufacturer"} for i in range(5)]
    found += [{"company_id": "plyco.com", "role": "Component Manufacturer"}, {"company_id": "x.com", "role": "Component Manufacturer"}]
    rows = role_extras(found, market, exclude={"r0.com"}, have=Counter({"Manufacturer": 10, "Reseller": 7}), n=10)
    ids = [r["company_id"] for r in rows]
    assert not any(i.startswith("m") for i in ids) and "plyco.com" not in ids and "r0.com" not in ids
    assert sum(i.startswith("r") for i in ids) == 3 and "x.com" in ids


def test_freeze_accepts_any_letter_case(tmp_path):
    sheet = tmp_path / "sheet.csv"
    sheet.write_text("company_id,name,label,note\na.com,A,supply reseller,\nb.com,B,SKIP,\nc.com,C,Manufacturer,ok\n")
    reference = tmp_path / "ref.json"
    assert freeze("m", sheet, ROLE_LABELS, reference) == 2
    assert [(l["company_id"], l["label"]) for l in load_labels(reference)] == [("a.com", "Supply Reseller"), ("c.com", "Manufacturer")]
