import pytest

from admitflow.normalize import (
    clean_text,
    name_key,
    normalize_course,
    normalize_email,
    normalize_name,
    normalize_phone,
    normalize_source,
)


@pytest.mark.parametrize(
    "raw, expected",
    [
        ("  Grace   Patel ", "Grace Patel"),
        ('Lee, Chloe', "Chloe Lee"),
        ("GRACE PATEL", "Grace Patel"),
        ("grace patel", "Grace Patel"),
        ("Nguyễn Thu", "Nguyễn Thu"),
        ("प्रिया शर्मा", "प्रिया शर्मा"),
        ("Seán O'Brien", "Seán O'Brien"),
        ("Ana-María López", "Ana-María López"),
        ("", ""),
        (None, ""),
    ],
)
def test_normalize_name(raw, expected):
    assert normalize_name(raw) == expected


def test_clean_text_unifies_unicode_forms():
    composed = "José"          # é as one character
    decomposed = "José"       # e + combining accent
    assert composed != decomposed
    assert clean_text(composed) == clean_text(decomposed)


def test_name_key_ignores_case_and_order_of_last_first():
    assert name_key("LEE, CHLOE") == name_key("Chloe Lee")


@pytest.mark.parametrize(
    "raw, expected",
    [
        ("+1 202-555-0141", "+12025550141"),
        ("(202) 555-0141", "+12025550141"),
        ("202.555.0141", "+12025550141"),
        ("2025550141", "+12025550141"),
        ("12025550141", "+12025550141"),
        ("+44 20 7946 0958", "+442079460958"),
        ("555-0141", None),
        ("", None),
        (None, None),
        ("+12", None),
    ],
)
def test_normalize_phone(raw, expected):
    assert normalize_phone(raw) == expected


@pytest.mark.parametrize(
    "raw, expected",
    [
        ("Grace.Patel91@Example.com ", "grace.patel91@example.com"),
        ("not-an-email", None),
        ("", None),
    ],
)
def test_normalize_email(raw, expected):
    assert normalize_email(raw) == expected


@pytest.mark.parametrize(
    "raw, expected",
    [
        ("DA", "Data Analytics"),
        ("nursing_assistant", "Nursing Assistance"),
        ("Digital Mktg", "Digital Marketing"),
        ("BBA", "Business Administration"),
        ("Data Analytics", "Data Analytics"),
        ("Robotics", "Robotics"),  # unknown courses are kept, not lost
        ("", None),
    ],
)
def test_normalize_course(raw, expected):
    assert normalize_course(raw) == expected


def test_normalize_source():
    assert normalize_source("Website ") == "website"
    assert normalize_source("Walk-in") == "walk-in"
    with pytest.raises(ValueError):
        normalize_source("carrier pigeon")
