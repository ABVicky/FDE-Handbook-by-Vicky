"""Ingestion pipeline and admissions matching (added in Module 05).

    extract  →  validate/normalize  →  load (dedupe)  →  audit
    (CSV)       (importers.py)         (SqlRepository)   (import_runs, rejected_rows)

Properties an FDE pipeline needs:
* **Idempotent:** re-running with the same file changes nothing (file checksum + dedupe).
* **Auditable:** every run is recorded with counts; every rejected row is kept with a reason.
* **Reconcilable:** rows read = rows loaded + rows merged + rows rejected.
"""
from __future__ import annotations

import csv
import hashlib
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from sqlalchemy import func, select, text

from .db import ImportRun, LeadRow, LeadSourceRow, RejectedRow, SqlRepository
from .importers import import_file
from .normalize import clean_text, name_key, normalize_email, normalize_name, normalize_phone


@dataclass
class RunReport:
    file_name: str
    status: str
    rows_read: int = 0
    rows_loaded: int = 0
    rows_merged: int = 0
    rows_rejected: int = 0

    def __str__(self) -> str:
        if self.status == "skipped":
            return f"{self.file_name}: skipped (already loaded)"
        return (
            f"{self.file_name}: read {self.rows_read}, new {self.rows_loaded}, "
            f"merged {self.rows_merged}, rejected {self.rows_rejected}"
        )


def sha256_of(path: Path) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def ingest(repo: SqlRepository, path: Path, fmt: str, *, force: bool = False) -> RunReport:
    path = Path(path)
    checksum = sha256_of(path)
    with repo.session() as s:
        already = s.scalar(
            select(ImportRun.id).where(ImportRun.file_sha256 == checksum, ImportRun.status == "succeeded").limit(1)
        )
    if already and not force:
        return RunReport(path.name, "skipped")

    with repo.session() as s, s.begin():
        run = ImportRun(file_name=path.name, file_sha256=checksum, fmt=fmt, started_at=datetime.now())
        s.add(run)
        s.flush()
        run_id = run.id

    result = import_file(path, fmt)
    added, merged = repo.add_leads(result.leads)

    report = RunReport(
        path.name,
        "succeeded",
        rows_read=len(result.leads) + len(result.rejected),
        rows_loaded=added,
        rows_merged=merged,
        rows_rejected=len(result.rejected),
    )
    assert report.rows_read == report.rows_loaded + report.rows_merged + report.rows_rejected  # reconciliation

    with repo.session() as s, s.begin():
        run = s.get(ImportRun, run_id)
        run.rows_read, run.rows_loaded = report.rows_read, report.rows_loaded
        run.rows_merged, run.rows_rejected = report.rows_merged, report.rows_rejected
        run.status = "succeeded"
        s.add_all(RejectedRow(run_id=run_id, line_num=line, reason=reason) for line, reason in result.rejected)
    return report


# -- matching admissions (student information system) to leads --------------------

@dataclass
class MatchReport:
    matched: int = 0
    already_matched: int = 0
    unmatched: List[Tuple[str, str]] = field(default_factory=list)  # (student_no, reason)


def _sis_phone(raw: str) -> Optional[str]:
    """The SIS sometimes stores a national trunk prefix: 02025550123 → +12025550123."""
    digits = "".join(ch for ch in raw if ch.isdigit())
    if len(digits) == 11 and digits.startswith("0"):
        digits = digits[1:]
    return normalize_phone(digits) if digits else None


def match_admissions(repo: SqlRepository, path: Path) -> MatchReport:
    """Mark leads as enrolled using the SIS export. Matching: email, else phone + name."""
    report = MatchReport()
    with open(path, newline="", encoding="utf-8-sig") as fh:
        rows = list(csv.DictReader(fh))
    with repo.session() as s, s.begin():
        for row in rows:
            student_no = clean_text(row["student_no"])
            if s.scalar(select(LeadRow.lead_id).where(LeadRow.student_no == student_no)):
                report.already_matched += 1
                continue
            email = normalize_email(row["email"])
            phone = _sis_phone(row["mobile"])
            key = name_key(normalize_name(row["full_name"]))  # "NAIR, Tom" → "tom nair"
            lead = None
            if email:
                lead = s.scalars(select(LeadRow).where(LeadRow.email == email).limit(1)).first()
            if lead is None and phone:
                lead = s.scalars(
                    select(LeadRow).where(LeadRow.phone == phone, LeadRow.name_key == key).limit(1)
                ).first()
            if lead is None:
                report.unmatched.append((student_no, "no lead with this email, or this phone and name"))
                continue
            lead.status = "enrolled"
            lead.student_no = student_no
            lead.enrolled_on = datetime.fromisoformat(row["enrolled_on"])
            report.matched += 1
    return report


# -- reporting -----------------------------------------------------------------------

CONVERSION_BY_CHANNEL_SQL = text(
    """
    SELECT s.source                                         AS channel,
           COUNT(*)                                         AS leads,
           SUM(CASE WHEN l.status = 'enrolled' THEN 1 ELSE 0 END) AS enrolled
    FROM leads AS l
    JOIN lead_sources AS s ON s.lead_id = l.lead_id
    GROUP BY s.source
    ORDER BY leads DESC
    """
)


def conversion_by_channel(repo: SqlRepository) -> List[Dict[str, object]]:
    """A lead counts once for each channel it used (so channel totals can exceed unique leads)."""
    with repo.session() as s:
        rows = s.execute(CONVERSION_BY_CHANNEL_SQL).mappings().all()
    return [
        {**row, "conversion": round(row["enrolled"] / row["leads"], 3) if row["leads"] else 0.0} for row in rows
    ]


def counts(repo: SqlRepository) -> Dict[str, int]:
    with repo.session() as s:
        return {
            "leads": s.scalar(select(func.count()).select_from(LeadRow)),
            "lead_sources": s.scalar(select(func.count()).select_from(LeadSourceRow)),
            "enrolled": s.scalar(select(func.count()).select_from(LeadRow).where(LeadRow.status == "enrolled")),
            "import_runs": s.scalar(select(func.count()).select_from(ImportRun)),
        }
