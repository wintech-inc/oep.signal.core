from signal_core.export import contact, homepage, merge_duplicates, phone_digits, split_address


def test_split_address():
    assert split_address("1201 County Rd 437, Cullman, AL 35055") == \
        {"street": "1201 County Rd 437", "city": "Cullman", "state": "AL", "zip": "35055"}
    assert split_address("12 Main St, Suite 4, Springdale, Arkansas 72762, United States") == \
        {"street": "12 Main St, Suite 4", "city": "Springdale", "state": "AR", "zip": "72762"}
    assert split_address("Cullman, AL") == {"street": "", "city": "Cullman", "state": "AL", "zip": ""}
    assert split_address("RR 1, Mitchell, ON N0K 1N0, Canada") == {"street": "", "city": "", "state": "", "zip": ""}
    assert split_address(None)["state"] == ""


def test_homepage():
    assert homepage("https://www.ranchkingblinds.com/blinds/x") == "https://www.ranchkingblinds.com"
    assert homepage("http://acme.com/") == "https://acme.com"
    assert homepage("https://facebook.com/AcmeBlinds") == "https://facebook.com/AcmeBlinds"
    assert homepage("https://facebook.com/AcmeBlinds", "https://acmeblinds.com/?utm_source=gmb") == "https://acmeblinds.com"
    assert homepage("https://facebook.com/AcmeBlinds", "https://www.facebook.com/AcmeBlinds/") == "https://facebook.com/AcmeBlinds"


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
            "ZIP": "", "_url": url}


def test_merge_duplicates_keeps_the_own_domain_row():
    rows = [
        row("Strand Ag Supply (Facebook)", "https://facebook.com/strandag", "https://facebook.com/strandag", "(555) 010-0000", "Ames"),
        row("Strand Ag Supply", "https://strandagsupply.com", "https://strandagsupply.com", "+1 555-010-0000"),
        row("Social Only", "https://facebook.com/x", "https://x.com"),
        row("X Co", "https://www.x.com", "https://www.x.com"),
        row("Alone", "https://alone.com", "https://alone.com", "(555) 999-0000"),
    ]
    kept, merged = merge_duplicates(rows)
    assert [r["Company"] for r in kept] == ["Strand Ag Supply", "X Co", "Alone"]
    assert kept[0]["City"] == "Ames"
    assert [(a["Company"], b["Company"]) for a, b in merged] == [
        ("Strand Ag Supply", "Strand Ag Supply (Facebook)"), ("X Co", "Social Only")]
    assert phone_digits("+1 (555) 010-0000") == phone_digits("555.010.0000") == "5550100000"
