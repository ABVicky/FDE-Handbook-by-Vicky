"""Find enquiries from the same person and merge them.

Rule (agreed with the Head of Admissions, see Module 03 build notes):
  * same lead ID                          -> same record (the file was imported twice)
  * same email address                    -> same person
  * same phone number AND same name       -> same person
  * same phone number only                -> NOT merged (families share phones)
"""
from __future__ import annotations

from typing import Dict, List, Tuple

from .models import Lead
from .normalize import name_key


def _merge(keep: Lead, other: Lead) -> None:
    """Merge `other` into `keep` (the earliest enquiry wins on conflicts)."""
    for source in other.sources:
        if source not in keep.sources:
            keep.sources.append(source)
    keep.phone = keep.phone or other.phone
    keep.email = keep.email or other.email
    keep.course = keep.course or other.course
    if other.notes and other.notes not in keep.notes:
        keep.notes = "; ".join(part for part in (keep.notes, other.notes) if part)


def dedupe(leads: List[Lead]) -> Tuple[List[Lead], int]:
    """Return (unique leads sorted by time, number of duplicates merged)."""
    by_id: Dict[str, Lead] = {}
    by_email: Dict[str, Lead] = {}
    by_phone_name: Dict[Tuple[str, str], Lead] = {}
    unique: List[Lead] = []
    merged = 0

    for lead in sorted(leads, key=lambda item: item.received_at):
        match = by_id.get(lead.lead_id)
        if match is None and lead.email:
            match = by_email.get(lead.email)
        if match is None and lead.phone:
            match = by_phone_name.get((lead.phone, name_key(lead.name)))

        if match is not None:
            _merge(match, lead)
            merged += 1
            target = match
        else:
            unique.append(lead)
            target = lead

        by_id.setdefault(lead.lead_id, target)
        if target.email:
            by_email.setdefault(target.email, target)
        if target.phone:
            by_phone_name.setdefault((target.phone, name_key(target.name)), target)

    return unique, merged
