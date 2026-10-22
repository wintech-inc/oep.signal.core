from signal_core.companies import Company
from signal_core.export import contact, crm_matches, crm_status, homepage, is_supplier, merge_duplicates, phone_digits, split_address


def test_split_address():
    assert split_address("1201 County Rd 437, Cullman, AL 35055") == \
        {"street": "1201 County Rd 437", "city": "Cullman", "state": "AL", "zip": "35055"}
    assert split_address("12 Main St, Suite 4, Springdale, Arkansas 72762, United States") == \
        {"street": "12 Main St, Suite 4", "city": "Springdale", "state": "AR", "zip": "72762"}
    assert split_address("Cullman, AL") == {"street": "", "city": "Cullman", "state": "AL", "zip": ""}
    assert split_address("RR 1, Mitchell, ON N0K 1N0, Canada") == {"street": "", "city": "", "state": "", "zip": ""}
    assert split_address(None)["state"] == ""


def test_homepage():
    assert homepage("https://www.ranchkingblinds.com/") == "https://www.ranchkingblinds.com"
    assert homepage("http://acme.com/") == "https://acme.com"
    assert homepage("https://facebook.com/AcmeBlinds") == "https://facebook.com/AcmeBlinds"
    assert homepage("https://facebook.com/AcmeBlinds", "https://acmeblinds.com/?utm_source=gmb") == "https://acmeblinds.com"
    assert homepage("https://facebook.com/AcmeBlinds", "https://www.facebook.com/AcmeBlinds/") == "https://facebook.com/AcmeBlinds"
    # A deep page may be someone else's site: the listing's website wins, else the page itself is kept.
    assert homepage("https://news.com/2024/acme-opens", "http://www.acmeblinds.com/home") == "https://www.acmeblinds.com"
    assert homepage("https://news.com/2024/acme-opens") == "https://news.com/2024/acme-opens"


def test_is_supplier():
    assert is_supplier("Pocahontas Aluminum", "Pocahontas Aluminum (PAC)")
    assert not is_supplier("Pocahontas Poultry Supply", "Pocahontas Aluminum (PAC)")


def test_contact_takes_the_matching_listing_only():
    places = [
        {"title": "Other Co", "address": "1 A St, Waco, TX 76701", "website": None, "phone": "(254) 555-0100", "cid": "1"},
        {"title": "Acme Blinds LLC", "address": "2 B St, Tyler, TX 75701", "website": None, "phone": "(903) 555-0101", "cid": "2"},
    ]
    found = contact(places, "acmeblinds.com", ["Acme Blinds"], None, "q")
    assert (found["city"], found["phone"], found["maps_url"]) == ("Tyler", "(903) 555-0101", "https://www.google.com/maps?cid=2")
    assert contact(places, "acmeblinds.com", ["Acme Blinds"], "OK", "q")["phone"] == ""   # listing in another state
    assert contact(places, "nobody.com", ["Nobody"], None, "q")["city"] == ""


def row(company, url, home, phone="", city=""):
    return {"Company": company, "Homepage": home, "Phone": phone, "City": city, "Street address": "", "State": "",
            "ZIP": "", "CRM Status": "", "_url": url}


def test_merge_duplicates_keeps_the_own_site_row():
    rows = [
        row("Strand Ag Supply", "https://facebook.com/strandag", "https://facebook.com/strandag", "(555) 010-0000", "Ames"),
        row("Strand Ag Supply Inc", "https://strandagsupply.com", "https://strandagsupply.com", "+1 555-010-0000"),
        row("X Co", "https://news.com/x-co-opens", "https://www.x.com"),
        row("X Co", "https://www.x.com", "https://www.x.com"),
        row("Redneck Blinds", "https://redneckblinds.com", "https://redneckblinds.com", "(555) 999-0000"),
        row("Black Dog Blinds", "https://blackdogblinds.com", "https://blackdogblinds.com", "(555) 999-0000"),
        row("Yoder Blinds", "https://instagram.com/yoderblinds", "https://instagram.com/yoderblinds"),
        row("Yoder Blinds", "https://www.yoderblinds.com", "https://www.yoderblinds.com", "(555) 222-0000"),
        row("Elite Buildings", "https://elite-a.com", "https://elite-a.com", "(555) 333-0000"),
        row("Elite Buildings", "https://elite-b.com", "https://elite-b.com", "(555) 444-0000"),
    ]
    kept, merged = merge_duplicates(rows)
    assert [r["Company"] for r in kept] == ["Strand Ag Supply Inc", "X Co", "Redneck Blinds", "Black Dog Blinds",
                                            "Yoder Blinds", "Elite Buildings", "Elite Buildings"]
    assert kept[0]["City"] == "Ames" and kept[1]["_url"] == "https://www.x.com"
    assert [(a["_url"], b["_url"]) for a, b in merged] == [
        ("https://strandagsupply.com", "https://facebook.com/strandag"), ("https://www.x.com", "https://news.com/x-co-opens"),
        ("https://www.yoderblinds.com", "https://instagram.com/yoderblinds")]
    assert phone_digits("+1 (555) 010-0000") == phone_digits("555.010.0000") == "5550100000"


def test_crm_status():
    assert crm_status([]) == ""
    company = Company(id="a.com", name="A", url="https://a.com",
                      crm=[{"market": "Poultry", "role": "Lead"}, {"market": "Agriculture", "role": "Lead"},
                           {"market": "Poultry", "role": "Customer"}])
    assert crm_status([company]) == "Customer; Lead"


def test_crm_matches_by_page_then_exact_name():
    a = Company(id="farmerboyag.com", name="Farmer Boy", url="https://farmerboyag.com", crm=[{"market": "Poultry", "role": "Lead"}])
    known, by_name = {a.id: a}, {"farmerboy": [a]}
    assert crm_matches({"company_id": "farmerboyag.com", "name": "x"}, known, by_name) == [a]
    assert crm_matches({"company_id": "facebook.com/farmerboyag", "name": "Farmer Boy", "url": "https://facebook.com/farmerboyag"},
                       known, by_name) == [a]
    assert crm_matches({"company_id": "other.com", "name": "Farmer Boy Sheds", "url": "https://other.com"}, known, by_name) == []
