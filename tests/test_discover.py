from signal_core import markets
from signal_core.companies import company_key
from signal_core.discover import (
    MAX_PAGE, QueryFile, add_found_by, first_queries, lead_url, nearby_queries, new_query, outside_geography, parse_town, settle,
    should_stop, title_name,
)

QUERIES = QueryFile(company_queries=["deer blind builder", "box blind manufacturer"], nearby_queries=["hunting blinds"],
                    list_queries=["hunting blind dealers list"], list_terms=["dealers"])


def test_lead_url():
    assert lead_url("https://www.facebook.com/KuduOutdoorProducts/posts/123") == "https://facebook.com/KuduOutdoorProducts"
    assert lead_url("https://www.facebook.com/groups/blinds") is None
    assert lead_url("https://www.instagram.com/acmeblinds/?hl=en") == "https://instagram.com/acmeblinds"
    assert lead_url("www.acme.com/x?y=1") == "https://www.acme.com/x"
    assert lead_url(None) is None


def test_social_lead_matches_seed_key():
    assert company_key(lead_url("https://m.facebook.com/KuduOutdoorProducts/photos")) == \
        company_key("https://www.facebook.com/KuduOutdoorProducts/")


def test_parse_town():
    assert parse_town("1201 County Rd 437, Cullman, AL 35055") == "Cullman, AL"
    assert parse_town("Springdale, Arkansas 72762, United States") == "Springdale, AR"
    assert parse_town("RR 1, Mitchell, ON N0K 1N0, Canada") == "Mitchell, ON"
    assert parse_town("Texas") is None and parse_town(None) is None


def test_title_name():
    assert title_name("Box Blinds - Texas Hunting Products", "https://texashuntingproducts.com/blinds") == "Texas Hunting Products"
    assert title_name("Kudu Outdoor Products | Facebook", "https://facebook.com/KuduOutdoorProducts") == "Kudu Outdoor Products"
    assert title_name("Home", "https://www.acme.com/") == "acme.com"
    assert title_name("At Northeast Agri systems we take pride in every house we build | Facebook",
                      "https://facebook.com/NortheastAgriSystems") == "Northeast Agri Systems"


def test_outside_geography():
    home, us = {"AL", "TX"}, {"US"}
    assert outside_geography({"url": "https://pwmaines.co.uk/", "location": None}, home, us) == "country domain .uk"
    assert outside_geography({"url": "https://acme.com/", "location": "Mitchell, ON"}, home, us)
    assert outside_geography({"url": "https://acme.com/", "location": "Anchorage, AK"}, home, us)
    assert not outside_geography({"url": "https://acme.co/", "location": "Cullman, AL"}, home, us)
    assert not outside_geography({"url": "https://acme.com/", "location": None}, home, us)
    assert outside_geography({"url": "https://acme.com/", "location": None, "country": "IN"}, home, us) == "country IN"
    assert not outside_geography({"url": "https://acme.com/", "location": None, "country": "US"}, home, us)
    assert not outside_geography({"url": "https://acme.de/", "location": "Mitchell, ON"}, set(), set())


def test_first_queries():
    queries = first_queries(QUERIES, ["Texas", "Ohio"], {"web", "maps", "lists"})
    texts = {(q["source"], q["q"]) for q in queries.values()}
    assert ("web", "deer blind builder") in texts and ("web", "deer blind builder in Ohio") in texts
    assert ("maps", "box blind manufacturer in Texas") in texts and ("maps", "box blind manufacturer") not in texts
    assert ("lists", "hunting blind dealers list") in texts
    assert len(queries) == 2 * 3 + 2 * 2 + 1
    assert all(q["due"] and q["page"] == 0 for q in queries.values())
    assert not any(q["source"] == "maps" for q in first_queries(QUERIES, ["Texas"], {"web"}).values())


def test_nearby_queries():
    queries = nearby_queries(QUERIES, "Cullman, AL")
    assert {(q["kind"], q["q"]) for q in queries.values()} == {
        ("maps", "hunting blinds near Cullman, AL"), ("web", "hunting blinds near Cullman, AL")}


def test_paging_rule():
    candidates = {"a.com": {"verdict": "in", "round": 2}, "b.com": {"verdict": "out", "round": 2},
                  "old.com": {"verdict": "in", "round": 1}, "new.com": {"verdict": None, "round": 2}}

    def fetched(keys, page=1):
        return {**new_query("web", "web", "q"), "page": page, "round": 2, "keys": keys, "settled": False, "due": False}

    q = fetched(["a.com", "b.com"])
    assert settle(q, candidates) and q["due"]                       # a new in-market company: next page
    q = fetched(["b.com", "old.com"])
    assert settle(q, candidates) and not q["due"]                   # only companies already known: stop
    q = fetched(["a.com"], page=MAX_PAGE)
    assert settle(q, candidates) and not q["due"]                   # deepest page reached
    q = fetched(["new.com"])
    assert not settle(q, candidates) and not q["settled"]           # wait until it is classified


def test_stop_rule():
    assert should_stop(0, 10) and should_stop(1, 100) and not should_stop(2, 100) and not should_stop(50, 50)


def test_found_by_merge():
    candidate = {"found_by": []}
    for source, detail in [("maps", "maps: x"), ("web", "web: y"), ("maps", "maps: x")]:
        add_found_by(candidate, source, detail)
    assert candidate["found_by"] == [{"source": "maps", "detail": "maps: x"}, {"source": "web", "detail": "web: y"}]


def test_query_files_are_not_markets():
    assert all("." not in m for m in markets.market_ids())
