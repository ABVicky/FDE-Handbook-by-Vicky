"""Exercise set 02 — reference solutions. Run: python3 ex02_collections.py"""
import unicodedata
from collections import Counter, defaultdict

LEADS = [
    {"name": "  GRACE PATEL ", "email": "Grace.Patel91@Example.com", "source": "Website ", "course": "Accounting"},
    {"name": "Lee, Chloe", "email": "chloe.lee95@example.com", "source": "website", "course": "DA"},
    {"name": "grace patel", "email": "grace.patel91@example.com", "source": "ad", "course": "Accounting"},
    {"name": "Nguyễn Thu", "email": "thu@example.org", "source": "ad", "course": "web_dev"},
    {"name": "प्रिया शर्मा", "email": "", "source": "WhatsApp", "course": "Nursing"},
    {"name": "José Chen", "email": "jose@example.org", "source": "ad", "course": "DA"},
]

COURSE_NAMES = {"DA": "Data Analytics", "web_dev": "Web Development", "Nursing": "Nursing Assistance"}


def clean_name(raw):
    name = " ".join(unicodedata.normalize("NFC", raw).split())
    if "," in name:
        last, _, first = name.partition(",")
        name = f"{first.strip()} {last.strip()}"
    if name.isupper() or name.islower():
        name = name.title()
    return name


def unique_emails_per_source(leads):
    emails = defaultdict(set)
    for lead in leads:
        source = lead["source"].strip().lower()
        emails[source]  # make sure sources with no emails still appear
        email = lead["email"].strip().lower()
        if email:
            emails[source].add(email)
    return {source: len(found) for source, found in emails.items()}


def courses(leads):
    return Counter(COURSE_NAMES.get(lead["course"], lead["course"]) for lead in leads)


def group_names_by_source(leads):
    groups = defaultdict(list)
    for lead in leads:
        groups[lead["source"].strip().lower()].append(clean_name(lead["name"]))
    return {source: sorted(names) for source, names in groups.items()}


def find_duplicates(leads):
    seen, duplicates = set(), []
    for lead in leads:
        email = lead["email"].strip().lower()
        if not email:
            continue
        if email in seen and email not in duplicates:
            duplicates.append(email)
        seen.add(email)
    return duplicates


# 6. `email in some_set` is O(1) on average (a hash lookup), so one pass over
#    1 million leads is ~1 million steps. `email in some_list` scans the list,
#    so the whole loop becomes O(n^2): up to ~500 billion comparisons.


if __name__ == "__main__":
    assert clean_name("  GRACE PATEL ") == "Grace Patel"
    assert clean_name("Lee, Chloe") == "Chloe Lee"
    assert clean_name("Nguyễn Thu") == "Nguyễn Thu"
    assert clean_name("प्रिया शर्मा") == "प्रिया शर्मा"
    assert clean_name("José Chen") == "José Chen"
    assert unique_emails_per_source(LEADS) == {"website": 2, "ad": 3, "whatsapp": 0}
    assert courses(LEADS) == {"Accounting": 2, "Data Analytics": 2, "Web Development": 1, "Nursing Assistance": 1}
    groups = group_names_by_source(LEADS)
    assert groups["ad"] == sorted(["Grace Patel", "Nguyễn Thu", "José Chen"])
    assert find_duplicates(LEADS) == ["grace.patel91@example.com"]
    print("all checks passed")
