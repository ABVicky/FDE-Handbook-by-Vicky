from datetime import datetime

from admitflow.dedupe import dedupe
from admitflow.models import Lead


def lead(lead_id, day, name, phone=None, email=None, source="website", course=None, notes=""):
    return Lead(lead_id, datetime(2026, 9, day), name, phone, email, course, [source], notes)


def test_same_email_is_merged_and_earliest_wins():
    later = lead("ad_1", 5, "Grace Patel", email="g@example.com", source="ad", course="Accounting")
    earlier = lead("ENQ-1", 1, "Grace Patel", email="g@example.com", phone="+12025550101")
    unique, merged = dedupe([later, earlier])
    assert merged == 1
    (person,) = unique
    assert person.lead_id == "ENQ-1"
    assert person.sources == ["website", "ad"]
    assert person.course == "Accounting"          # filled in from the later enquiry
    assert person.phone == "+12025550101"


def test_same_phone_and_name_is_merged():
    unique, merged = dedupe(
        [
            lead("ENQ-1", 1, "Daniel Okoye", phone="+12025550163"),
            lead("WALKIN-1", 3, "DANIEL OKOYE", phone="+12025550163", source="walk-in", notes="came with parent"),
        ]
    )
    assert merged == 1
    assert unique[0].sources == ["website", "walk-in"]
    assert unique[0].notes == "came with parent"


def test_shared_phone_different_names_is_not_merged():
    unique, merged = dedupe(
        [
            lead("ENQ-1", 1, "Amara Costa", phone="+12025550174"),
            lead("ENQ-2", 2, "Zara Costa", phone="+12025550174"),  # sisters, one phone
        ]
    )
    assert merged == 0
    assert len(unique) == 2


def test_merge_chain_across_three_channels():
    unique, merged = dedupe(
        [
            lead("ENQ-1", 1, "Elena Lee", phone="+12025550157", email="e@example.com"),
            lead("ad_1", 2, "elena lee", phone="+12025550157", email="E@example.com".lower(), source="ad"),
            lead("WALKIN-1", 4, "ELENA LEE", phone="+12025550157", source="walk-in"),
        ]
    )
    assert merged == 2
    assert unique[0].sources == ["website", "ad", "walk-in"]


def test_same_channel_twice_is_not_listed_twice():
    unique, _ = dedupe(
        [lead("A", 1, "Sam Costa", email="s@example.com"), lead("B", 2, "Sam Costa", email="s@example.com")]
    )
    assert unique[0].sources == ["website"]
