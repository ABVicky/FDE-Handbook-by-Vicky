"""Exercise set 04 — reference solution. Tests: python3 -m pytest test_ex04_followup.py"""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List


@dataclass
class FollowUp:
    lead_id: str
    due: datetime
    counsellor: str
    done: bool = False
    notes: List[str] = field(default_factory=list)

    def is_overdue(self, now: datetime) -> bool:
        return not self.done and self.due < now

    def complete(self, note: str) -> None:
        if self.done:
            raise ValueError("already done")
        self.done = True
        self.notes.append(note)


def overdue(followups: List[FollowUp], now: datetime) -> List[FollowUp]:
    return sorted((f for f in followups if f.is_overdue(now)), key=lambda f: f.due)


def per_counsellor(followups: List[FollowUp], now: datetime) -> Dict[str, int]:
    return dict(Counter(f.counsellor for f in followups if f.is_overdue(now)))
