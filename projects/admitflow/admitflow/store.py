"""Save and load leads as a JSON file. (Module 05 replaces this with PostgreSQL.)"""
from __future__ import annotations

import csv
import json
import os
from pathlib import Path
from typing import List

from .models import Lead

DEFAULT_STORE = "leads.json"
EXPORT_FIELDS = ["lead_id", "received_at", "name", "phone", "email", "course", "sources", "status", "assigned_to", "crm_id", "notes"]


def store_path() -> Path:
    """The store location comes from ADMITFLOW_STORE, so it's configurable per environment."""
    return Path(os.environ.get("ADMITFLOW_STORE", DEFAULT_STORE))


def _read(path: Path):
    if not path.exists():
        return {"leads": []}
    with open(path, encoding="utf-8") as fh:
        data = json.load(fh)
    # Module 03 stores were a plain list; from Module 04 the file also holds users, notes, follow-ups.
    return {"leads": data} if isinstance(data, list) else data


def load(path: Path) -> List[Lead]:
    return [Lead.from_dict(item) for item in _read(path).get("leads", [])]


def save(path: Path, leads: List[Lead]) -> None:
    data = _read(path)  # keep users, notes and follow-ups written by the API
    data["leads"] = [lead.to_dict() for lead in leads]
    # Write to a temporary file, then rename: a crash mid-write can't corrupt the store.
    tmp = path.with_name(path.name + ".tmp")
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)
    tmp.replace(path)


def export_csv(path: Path, leads: List[Lead]) -> None:
    # utf-8-sig so Excel shows names like "Nguyễn" correctly when counsellors open it.
    with open(path, "w", newline="", encoding="utf-8-sig") as fh:
        writer = csv.DictWriter(fh, fieldnames=EXPORT_FIELDS)
        writer.writeheader()
        for lead in leads:
            row = lead.to_dict()
            row["sources"] = "|".join(lead.sources)
            writer.writerow(row)
