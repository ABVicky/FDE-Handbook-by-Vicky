"""Data access behind an interface (added in Module 04).

The API talks to a `Repository`, never to files or databases directly. Module 04
uses `JsonRepository` (one JSON file); Module 05 adds `SqlRepository`
(PostgreSQL/SQLite) with the same methods, so the API code doesn't change.
"""
from __future__ import annotations

import json
import os
import threading
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Protocol, Tuple

from .dedupe import dedupe
from .models import AuditEvent, Draft, FollowUp, Lead, Note, User


class Repository(Protocol):
    def list_leads(
        self,
        *,
        status: Optional[str] = None,
        source: Optional[str] = None,
        assigned_to: Optional[str] = None,
        search: Optional[str] = None,
        offset: int = 0,
        limit: int = 50,
    ) -> Tuple[List[Lead], int]: ...

    def get_lead(self, lead_id: str) -> Optional[Lead]: ...

    def add_leads(self, leads: List[Lead]) -> Tuple[int, int]: ...

    def update_lead(self, lead: Lead) -> None: ...

    def add_note(self, note: Note) -> None: ...

    def notes_for(self, lead_id: str) -> List[Note]: ...

    def add_followup(self, lead_id: str, counsellor: str, due: datetime) -> FollowUp: ...

    def followups(self, *, counsellor: Optional[str] = None, due_before: Optional[datetime] = None) -> List[FollowUp]: ...

    def complete_followup(self, followup_id: str) -> Optional[FollowUp]: ...

    def get_user(self, username: str) -> Optional[User]: ...

    def save_user(self, user: User) -> None: ...

    def save_draft(self, draft: Draft) -> None: ...

    def get_draft(self, draft_id: str) -> Optional[Draft]: ...

    def list_drafts(self, *, status: Optional[str] = None, lead_id: Optional[str] = None) -> List[Draft]: ...

    def record_event(self, event_id: str) -> bool:
        """Remember an incoming event ID. Returns False if it was already processed (idempotency)."""
        ...

    def add_audit(self, event: AuditEvent) -> None: ...

    def list_audit(self, *, actor: Optional[str] = None, action: Optional[str] = None,
                   limit: int = 100) -> List[AuditEvent]: ...


def filter_leads(leads, *, status=None, source=None, assigned_to=None, search=None):
    """Shared filtering logic, so every repository behaves identically."""
    result = leads
    if status:
        result = [lead for lead in result if lead.status == status]
    if source:
        result = [lead for lead in result if source in lead.sources]
    if assigned_to:
        result = [lead for lead in result if lead.assigned_to == assigned_to]
    if search:
        result = [lead for lead in result if lead.matches(search)]
    return result


class JsonRepository:
    """Everything in one JSON file. Fine for a pilot with a few users; not for production."""

    def __init__(self, path: Path):
        self.path = Path(path)
        self._lock = threading.Lock()  # FastAPI may serve requests on several threads

    # -- file handling -------------------------------------------------
    def _load(self) -> Dict[str, list]:
        if not self.path.exists():
            return {"leads": [], "notes": [], "followups": [], "users": [], "drafts": [], "events": [], "audit": []}
        data = json.loads(self.path.read_text(encoding="utf-8"))
        if isinstance(data, list):  # a Module 03 store: just a list of leads
            data = {"leads": data}
        for key in ("leads", "notes", "followups", "users", "drafts", "events", "audit"):
            data.setdefault(key, [])
        return data

    def _save(self, data: Dict[str, list]) -> None:
        tmp = self.path.with_name(self.path.name + ".tmp")
        tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        tmp.replace(self.path)

    def _leads(self, data) -> List[Lead]:
        return [Lead.from_dict(item) for item in data["leads"]]

    # -- leads -----------------------------------------------------------
    def list_leads(self, *, status=None, source=None, assigned_to=None, search=None, offset=0, limit=50):
        leads = filter_leads(
            self._leads(self._load()), status=status, source=source, assigned_to=assigned_to, search=search
        )
        leads.sort(key=lambda lead: lead.received_at, reverse=True)
        return leads[offset : offset + limit], len(leads)

    def get_lead(self, lead_id):
        return next((lead for lead in self._leads(self._load()) if lead.lead_id == lead_id), None)

    def add_leads(self, leads):
        with self._lock:
            data = self._load()
            existing = self._leads(data)
            unique, merged = dedupe(existing + list(leads))
            data["leads"] = [lead.to_dict() for lead in unique]
            self._save(data)
            return len(unique) - len(existing), merged

    def update_lead(self, lead):
        with self._lock:
            data = self._load()
            data["leads"] = [lead.to_dict() if item["lead_id"] == lead.lead_id else item for item in data["leads"]]
            self._save(data)

    # -- notes -----------------------------------------------------------
    def add_note(self, note):
        with self._lock:
            data = self._load()
            data["notes"].append(note.to_dict())
            self._save(data)

    def notes_for(self, lead_id):
        notes = [Note.from_dict(n) for n in self._load()["notes"] if n["lead_id"] == lead_id]
        return sorted(notes, key=lambda note: note.created_at)  # same order as SqlRepository (contract test)

    # -- follow-ups ------------------------------------------------------
    def add_followup(self, lead_id, counsellor, due):
        followup = FollowUp(uuid.uuid4().hex[:12], lead_id, counsellor, due)
        with self._lock:
            data = self._load()
            data["followups"].append(followup.to_dict())
            self._save(data)
        return followup

    def followups(self, *, counsellor=None, due_before=None):
        items = [FollowUp.from_dict(f) for f in self._load()["followups"]]
        if counsellor:
            items = [f for f in items if f.counsellor == counsellor]
        if due_before:
            items = [f for f in items if not f.done and f.due <= due_before]
        return sorted(items, key=lambda f: f.due)

    def complete_followup(self, followup_id):
        with self._lock:
            data = self._load()
            for item in data["followups"]:
                if item["followup_id"] == followup_id:
                    item["done"] = True
                    self._save(data)
                    return FollowUp.from_dict(item)
        return None

    # -- users -----------------------------------------------------------
    def get_user(self, username):
        return next((User(**u) for u in self._load()["users"] if u["username"] == username), None)

    def save_user(self, user):
        with self._lock:
            data = self._load()
            data["users"] = [u for u in data["users"] if u["username"] != user.username] + [user.to_dict()]
            self._save(data)

    # -- drafts (Module 08) ----------------------------------------------------------
    def save_draft(self, draft):
        with self._lock:
            data = self._load()
            data["drafts"] = [d for d in data["drafts"] if d["draft_id"] != draft.draft_id] + [draft.to_dict()]
            self._save(data)

    def get_draft(self, draft_id):
        return next((Draft.from_dict(d) for d in self._load()["drafts"] if d["draft_id"] == draft_id), None)

    def list_drafts(self, *, status=None, lead_id=None):
        drafts = [Draft.from_dict(d) for d in self._load()["drafts"]]
        drafts = [d for d in drafts if (status is None or d.status == status) and (lead_id is None or d.lead_id == lead_id)]
        return sorted(drafts, key=lambda d: d.created_at)

    # -- processed events (Module 09) --------------------------------------------------
    def record_event(self, event_id):
        with self._lock:
            data = self._load()
            if event_id in data["events"]:
                return False
            data["events"].append(event_id)
            self._save(data)
            return True

    # -- audit log (Module 10) ------------------------------------------------------------
    def add_audit(self, event):
        with self._lock:
            data = self._load()
            data["audit"].append(event.to_dict())
            self._save(data)

    def list_audit(self, *, actor=None, action=None, limit=100):
        events = [AuditEvent.from_dict(e) for e in self._load()["audit"]]
        events = [e for e in events if (actor is None or e.actor == actor) and (action is None or e.action.startswith(action))]
        return sorted(events, key=lambda e: e.at, reverse=True)[:limit]


def default_repository() -> "Repository":
    """Chosen by configuration: DATABASE_URL → SqlRepository (Module 05), else the JSON file."""
    database_url = os.environ.get("DATABASE_URL")
    if database_url:
        from .db import SqlRepository  # imported lazily: SQLAlchemy is optional

        return SqlRepository(database_url)
    return JsonRepository(Path(os.environ.get("ADMITFLOW_STORE", "leads.json")))
