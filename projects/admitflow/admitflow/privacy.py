"""Personal-data handling helpers (added in Module 10).

`redact` masks email addresses and phone numbers in free text. Used (1) in log messages, via
`RedactingFilter`, and (2) on notes before they're sent to a language model.
"""
from __future__ import annotations

import logging
import re

EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
PHONE = re.compile(r"(?<![\w(])(?:\+|\()?\d[\d\s().-]{7,}\d(?!\w)")
DATE_LIKE = re.compile(r"\d{4}-\d{2}-\d{2}|\d{1,2}[:/]\d{2}")


def _mask_phone(match: re.Match) -> str:
    text = match.group(0)
    digits = sum(ch.isdigit() for ch in text)
    if not 10 <= digits <= 15 or DATE_LIKE.search(text):   # dates, times and IDs aren't phone numbers
        return text
    return "[phone]"


def mask_email(match: re.Match) -> str:
    local, _, domain = match.group(0).partition("@")
    return f"{local[:1]}***@{domain}"


def redact(text: str) -> str:
    """'Call 202 555 0141 or grace@example.com' → 'Call [phone] or g***@example.com'."""
    if not text:
        return text
    return PHONE.sub(_mask_phone, EMAIL.sub(mask_email, text))


class RedactingFilter(logging.Filter):
    """Masks emails and phone numbers in every log record that passes through it."""

    def filter(self, record: logging.LogRecord) -> bool:
        message = record.getMessage()
        redacted = redact(message)
        if redacted != message:
            record.msg, record.args = redacted, None
        return True
