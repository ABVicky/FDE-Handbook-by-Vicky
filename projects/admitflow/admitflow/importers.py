"""Read each channel's export format and turn it into Lead objects.

Each channel has different columns, date formats and quirks. Keeping one
importer per format means a change in one export doesn't break the others.
"""
from __future__ import annotations

import csv
import logging
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Callable, Dict, Iterator, List, Tuple

from .models import Lead
from .normalize import (
    clean_text,
    normalize_course,
    normalize_email,
    normalize_name,
    normalize_phone,
    normalize_source,
)

log = logging.getLogger(__name__)


@dataclass
class ImportResult:
    leads: List[Lead] = field(default_factory=list)
    rejected: List[Tuple[int, str]] = field(default_factory=list)  # (line number, reason)


def _rows(path: Path) -> Iterator[Tuple[int, Dict[str, str]]]:
    # utf-8-sig silently removes the byte-order mark (BOM) Excel adds to CSV files.
    with open(path, newline="", encoding="utf-8-sig") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            if not any((value or "").strip() for value in row.values()):
                continue  # blank line
            yield reader.line_num, row


def _website(row: Dict[str, str]) -> Lead:
    return Lead(
        lead_id=clean_text(row["enquiry_id"]),
        received_at=datetime.strptime(clean_text(row["received_at"]), "%Y-%m-%d %H:%M"),
        name=normalize_name(row["name"]),
        phone=normalize_phone(row["phone"]),
        email=normalize_email(row["email"]),
        course=normalize_course(row["course"]),
        sources=[normalize_source(row["source"])],
    )


def _ads(row: Dict[str, str]) -> Lead:
    created = datetime.strptime(clean_text(row["created_time"]), "%Y-%m-%dT%H:%M:%SZ")
    return Lead(
        lead_id=clean_text(row["lead_id"]),
        received_at=created,
        name=normalize_name(row["full_name"]),
        phone=normalize_phone(row["phone_number"]),
        email=normalize_email(row["email"]),
        course=normalize_course(row["program_interest"]),
        sources=["ad"],
        notes=f"campaign: {clean_text(row['campaign_name'])}",
    )


def _walkins(row: Dict[str, str]) -> Lead:
    contact = clean_text(row["Contact"])
    email = normalize_email(contact) if "@" in contact else None
    phone = None if email else normalize_phone(contact)
    received = datetime.strptime(clean_text(row["Date"]), "%d/%m/%Y")  # day first!
    return Lead(
        lead_id="",  # paper forms have no ID; assigned below
        received_at=received,
        name=normalize_name(row["Name"]),
        phone=phone,
        email=email,
        course=normalize_course(row["Course"]),
        sources=["walk-in"],
        notes=clean_text(row.get("Notes")),
    )


FORMATS: Dict[str, Callable[[Dict[str, str]], Lead]] = {
    "website": _website,
    "ads": _ads,
    "walkins": _walkins,
}


def import_file(path: Path, fmt: str) -> ImportResult:
    """Import one file. Bad rows are collected with a reason, never silently dropped."""
    if fmt not in FORMATS:
        raise ValueError(f"unknown format {fmt!r}; choose from {', '.join(FORMATS)}")
    parse = FORMATS[fmt]
    result = ImportResult()
    for line_num, row in _rows(path):
        try:
            lead = parse(row)
        except (KeyError, ValueError) as exc:
            result.rejected.append((line_num, f"{type(exc).__name__}: {exc}"))
            log.warning("%s line %d rejected: %s", path.name, line_num, exc)
            continue
        if not lead.lead_id:
            lead.lead_id = f"WALKIN-{line_num:04d}"
        if not lead.name:
            result.rejected.append((line_num, "missing name"))
            continue
        if not (lead.phone or lead.email):
            log.info("%s line %d has no usable contact details", path.name, line_num)
        result.leads.append(lead)
    return result
