"""The Lead data model."""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class Lead:
    """One prospective student's enquiry, after normalization.

    `sources` is a list because the same person often enquires through several
    channels; deduplication merges them into one Lead.
    """

    lead_id: str
    received_at: datetime
    name: str
    phone: Optional[str]
    email: Optional[str]
    course: Optional[str]
    sources: List[str] = field(default_factory=list)
    notes: str = ""
    status: str = "new"                 # see LEAD_STATUSES (added in Module 04)
    assigned_to: Optional[str] = None   # counsellor username (added in Module 04)
    crm_id: Optional[str] = None        # the contact's ID in the CRM, once synced (added in Module 09)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["received_at"] = self.received_at.isoformat(timespec="minutes")
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Lead":
        data = dict(data)
        data["received_at"] = datetime.fromisoformat(data["received_at"])
        return cls(**data)

    def matches(self, text: str) -> bool:
        """Case-insensitive search across the fields counsellors search by."""
        needle = text.casefold()
        haystack = " ".join(
            value for value in (self.name, self.email, self.phone, self.course, self.lead_id) if value
        ).casefold()
        return needle in haystack


LEAD_STATUSES = ("new", "contacted", "visit_booked", "applied", "enrolled", "lost")


@dataclass
class Note:
    lead_id: str
    author: str
    text: str
    created_at: datetime

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["created_at"] = self.created_at.isoformat(timespec="seconds")
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Note":
        data = dict(data)
        data["created_at"] = datetime.fromisoformat(data["created_at"])
        return cls(**data)


@dataclass
class FollowUp:
    followup_id: str
    lead_id: str
    counsellor: str
    due: datetime
    done: bool = False

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["due"] = self.due.isoformat(timespec="minutes")
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FollowUp":
        data = dict(data)
        data["due"] = datetime.fromisoformat(data["due"])
        return cls(**data)


@dataclass
class User:
    username: str
    full_name: str
    role: str            # "counsellor" or "admin"
    password_hash: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


DRAFT_STATUSES = ("pending_approval", "approved", "rejected", "sent")


@dataclass
class Draft:
    """A follow-up message written by the assistant. It can only be sent after a person approves it."""

    draft_id: str
    lead_id: str
    channel: str                 # "email" or "whatsapp"
    subject: str
    body: str
    requested_by: str            # the counsellor who asked for the draft
    created_at: datetime
    engine: str = "offline"      # which model wrote it
    status: str = "pending_approval"
    decided_by: Optional[str] = None
    decided_at: Optional[datetime] = None
    reason: str = ""
    sent_at: Optional[datetime] = None      # Module 09: set by the outbox after a successful send
    external_id: Optional[str] = None       # the messaging provider's message ID

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        for key in ("created_at", "decided_at", "sent_at"):
            value = getattr(self, key)
            data[key] = value.isoformat(timespec="seconds") if value else None
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Draft":
        data = dict(data)
        data["created_at"] = datetime.fromisoformat(data["created_at"])
        for key in ("decided_at", "sent_at"):
            data[key] = datetime.fromisoformat(data[key]) if data.get(key) else None
        return cls(**data)


@dataclass
class AuditEvent:
    """Who did what, when (Module 10). Append-only: never updated or deleted by the application."""

    at: datetime
    actor: str          # username, or a system name such as "website" or "outbox"
    action: str         # e.g. "auth.login.failed", "lead.assign", "draft.approve"
    target: str = ""    # e.g. a lead or draft ID (never contact details)
    details: str = ""

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["at"] = self.at.isoformat(timespec="seconds")
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AuditEvent":
        data = dict(data)
        data["at"] = datetime.fromisoformat(data["at"])
        return cls(**data)
