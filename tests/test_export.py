from signal_core.companies import Company
from signal_core.export import (
    abroad, contact, crm_matches, us_phone, crm_status, homepage, is_supplier, merge_duplicates, names_site, phone_digits, split_address,
)


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
    # The website stage 2 found in the evidence wins.
    assert homepage("https://facebook.com/AcmeBlinds", "https://acmeblinds.com", "https://other.com") == "https://acmeblinds.com"
    # A map listing's website only when it is named after the company.
    assert homepage("https://facebook.com/AcmeBlinds", "", "https://acmeblinds.com/?utm_source=gmb", "Acme Blinds") == "https://acmeblinds.com"
    assert homepage("https://instagram.com/lazymanoutdoors", "", "https://printkindred.com/", "Lazy Man Outdoors") == \
        "https://instagram.com/lazymanoutdoors"
    assert homepage("https://facebook.com/AcmeBlinds", "", "https://www.facebook.com/AcmeBlinds/", "Acme") == "https://facebook.com/AcmeBlinds"
    # A deep page: its root when the site is named after the company, else the listing's website, else the page.
    assert homepage("https://www.bigdutchmanusa.com/en/egg-production/", "", None, "Big Dutchman") == "https://www.bigdutchmanusa.com"
    assert homepage("https://news.com/2024/acme-opens", "", "http://www.acmeblinds.com/home", "Acme Blinds") == "https://www.acmeblinds.com"
    assert homepage("https://news.com/2024/acme-opens", "", None, "Acme Blinds") == "https://news.com/2024/acme-opens"
    assert homepage("https://epsbuildings.com/our-company/", "", "https://www.epsbuildings.com/", "Energy Panel Structures") == \
        "https://www.epsbuildings.com"


def test_names_site():
    assert names_site("45North", "https://www.45northme.com")
    assert names_site("ChickenHouses.com", "https://chickenhouses.com")
    assert not names_site("45North", "https://www.sugarloaf.com")
    assert not names_site("Lazy Man Outdoors", "https://printkindred.com")


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
    # A listing whose website is another site than the company's own is a same-named business.
    places[1]["website"] = "http://acmeblindsnj.com/"
    assert contact(places, "acmeblinds.com", ["Acme Blinds"], None, "q", "https://acmeblinds.com")["phone"] == ""
    assert contact(places, "acmeblinds.com", ["Acme Blinds"], None, "q")["phone"] == "(903) 555-0101"
    # A phone field that isn't a phone number is dropped.
    places[1]["phone"] = "29800 135th Ave"
    assert contact(places, "acmeblinds.com", ["Acme Blinds"], None, "q")["phone"] == ""


def test_abroad():
    home = {"TX", "AL"}
    assert abroad({}, home) is None
    assert abroad({"based_in": "Waco, TX", "based_country": "US"}, home) is None
    assert "India" in abroad({"based_in": "Pune", "based_country": "India"}, home)
    assert "Anchorage, AK" in abroad({"based_in": "Anchorage, AK", "based_country": "US"}, home)
    assert "map listing address" in abroad({"contact": {"address": "12 Pembina Hwy, Winnipeg, MB R3T 2N2", "state": ""}}, home)
    assert abroad({"contact": {"address": "1845 US-62", "state": ""}}, home) is None   # a street only
    assert abroad({"contact": {"address": "12 Main St, San Antonio", "state": ""}}, home) is None
    assert "+44" in abroad({"contact": {"address": "", "phone": "+44 1568 708819"}}, home)
    assert abroad({"contact": {"address": "", "phone": "+1 254-555-0100"}}, home) is None
    # Stage 2 placing it in a home state wins over a parent company's foreign number.
    assert abroad({"based_in": "Luverne, AL", "based_country": "US", "site_contact": {"source": "website", "phone": "+39 0444 000000"}}, home) is None
    assert "Canada" in abroad({"site_contact": {"source": "website", "country": "Canada"}}, home)


def row(company, url, home, phone="", city="", state=""):
    return {"Company": company, "Homepage": home, "Phone": phone, "City": city, "Street address": "", "State": state,
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
        row("PA Deer Blinds", "https://www.padeerblinds.com", "https://www.padeerblinds.com", "(555) 555-0000"),
        row("Pennsylvania Deer Blinds", "https://instagram.com/padeerblinds", "https://instagram.com/padeerblinds"),
        row("Formex Manufacturing, Inc.", "https://www.formex.com", "https://www.formex.com", "(555) 600-0000", state="GA"),
        row("Formex Manufacturing", "https://snaplockblinds.com", "https://snaplockblinds.com", "(555) 600-1111", state="GA"),
        row("Orion Hunting Products", "https://huntorion.com", "https://huntorion.com", "(555) 700-0000"),
        row("Orion Hunting Blinds", "https://facebook.com/61575049126137", "https://facebook.com/61575049126137", "(555) 700-0000"),
    ]
    kept, merged = merge_duplicates(rows)
    assert [r["Company"] for r in kept] == ["Strand Ag Supply Inc", "X Co", "Redneck Blinds", "Black Dog Blinds",
                                            "Yoder Blinds", "Elite Buildings", "Elite Buildings", "PA Deer Blinds",
                                            "Formex Manufacturing, Inc.", "Orion Hunting Products"]
    assert kept[0]["City"] == "Ames" and kept[1]["_url"] == "https://www.x.com"
    assert [(a["_url"], b["_url"]) for a, b in merged] == [
        ("https://strandagsupply.com", "https://facebook.com/strandag"), ("https://www.x.com", "https://news.com/x-co-opens"),
        ("https://www.yoderblinds.com", "https://instagram.com/yoderblinds"),
        ("https://www.padeerblinds.com", "https://instagram.com/padeerblinds"),
        ("https://www.formex.com", "https://snaplockblinds.com"), ("https://huntorion.com", "https://facebook.com/61575049126137")]
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


def test_us_phone():
    assert us_phone("+1 (270) 748-2541") == us_phone("270.748.2541") == us_phone("1-270-748-2541") == "270-748-2541"
    assert us_phone("(254)725-4554 ext. 12") == "254-725-4554"
    assert us_phone("+44 1568 708819") == us_phone("1300-655-735 (AUS)") == us_phone("018 462 0784") == us_phone("") == ""
