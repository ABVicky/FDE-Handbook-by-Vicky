"""Turn messy, channel-specific values into one consistent format.

Every function here is pure (no files, no network), which makes them easy to test.
"""
from __future__ import annotations

import re
import unicodedata
from typing import Optional

COURSES = {
    "data analytics": "Data Analytics",
    "data_analytics": "Data Analytics",
    "da": "Data Analytics",
    "digital marketing": "Digital Marketing",
    "digital_marketing": "Digital Marketing",
    "digital mktg": "Digital Marketing",
    "dm": "Digital Marketing",
    "accounting": "Accounting",
    "accounts": "Accounting",
    "nursing assistance": "Nursing Assistance",
    "nursing_assistant": "Nursing Assistance",
    "nursing": "Nursing Assistance",
    "nursing asst": "Nursing Assistance",
    "web development": "Web Development",
    "web_dev": "Web Development",
    "web dev": "Web Development",
    "web": "Web Development",
    "business administration": "Business Administration",
    "business_admin": "Business Administration",
    "business admin": "Business Administration",
    "bba": "Business Administration",
}

SOURCES = {"website", "ad", "phone", "walk-in", "whatsapp"}


def clean_text(value: Optional[str]) -> str:
    """Strip, collapse internal whitespace, and use one Unicode form (NFC).

    NFC matters: "é" can be stored as one character or as "e" + an accent mark.
    Without normalizing, two identical-looking names would not compare equal.
    """
    if value is None:
        return ""
    value = unicodedata.normalize("NFC", value)
    return " ".join(value.split())


def normalize_name(value: Optional[str]) -> str:
    """'  LEE, CHLOE ' -> 'Chloe Lee'. Keeps any script: 'प्रिया शर्मा', 'Nguyễn'."""
    name = clean_text(value)
    if "," in name:
        last, _, first = name.partition(",")
        name = f"{first.strip()} {last.strip()}".strip()
    # Only change capitalization if the whole name is shouted or all lower-case;
    # otherwise respect how the person wrote it (e.g. "McDonald", "de Souza").
    if name.isupper() or name.islower():
        name = name.title()
    return name


def name_key(value: Optional[str]) -> str:
    """A comparison key: case-insensitive and ignoring word order differences of 'Last, First'."""
    return normalize_name(value).casefold()


def normalize_phone(value: Optional[str], default_country: str = "1") -> Optional[str]:
    """Return digits in E.164 style (+12025550123), or None if it isn't a usable number.

    This handles the formats seen in AdmitFlow data. Real projects should use a
    dedicated library (e.g. `phonenumbers`), because numbering rules vary by country.
    """
    text = clean_text(value)
    if not text:
        return None
    has_plus = text.startswith("+")
    digits = re.sub(r"\D", "", text)
    if has_plus:
        return f"+{digits}" if 8 <= len(digits) <= 15 else None
    if len(digits) == 10:
        return f"+{default_country}{digits}"
    if len(digits) == 11 and digits.startswith(default_country):
        return f"+{digits}"
    return None


def normalize_email(value: Optional[str]) -> Optional[str]:
    email = clean_text(value).lower()
    if re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
        return email
    return None


def normalize_course(value: Optional[str]) -> Optional[str]:
    """Map abbreviations and channel-specific codes to the official course name."""
    key = clean_text(value).lower()
    if not key:
        return None
    return COURSES.get(key, clean_text(value))


def normalize_source(value: Optional[str]) -> str:
    source = clean_text(value).lower()
    if source not in SOURCES:
        raise ValueError(f"unknown source: {value!r}")
    return source
