"""SQL storage with SQLAlchemy 2.0 (added in Module 05).

Works with PostgreSQL in production (`postgresql+psycopg://user:pass@host/db`) and SQLite for
local development and tests (`sqlite:///admitflow.db`). Implements the same `Repository`
interface as `JsonRepository`, so the API and CLI don't change.
"""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import List, Optional, Tuple

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    create_engine,
    func,
    or_,
    select,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, relationship, selectinload

from .dedupe import _merge
from .models import AuditEvent, Draft, FollowUp, Lead, Note, User
from .normalize import name_key


class Base(DeclarativeBase):
    pass


class LeadRow(Base):
    __tablename__ = "leads"

    lead_id: Mapped[str] = mapped_column(String(40), primary_key=True)
    received_at: Mapped[datetime] = mapped_column(DateTime, index=True)
    name: Mapped[str] = mapped_column(String(200))
    name_key: Mapped[str] = mapped_column(String(200))           # casefolded, for matching
    phone: Mapped[Optional[str]] = mapped_column(String(20))
    email: Mapped[Optional[str]] = mapped_column(String(254), index=True)
    course: Mapped[Optional[str]] = mapped_column(String(100))
    status: Mapped[str] = mapped_column(String(20), default="new", index=True)
    assigned_to: Mapped[Optional[str]] = mapped_column(ForeignKey("users.username"), index=True)
    notes: Mapped[str] = mapped_column(Text, default="")
    student_no: Mapped[Optional[str]] = mapped_column(String(20), unique=True)  # set when matched to an admission
    enrolled_on: Mapped[Optional[datetime]] = mapped_column(DateTime)
    crm_id: Mapped[Optional[str]] = mapped_column(String(64))   # Module 09; unique via a *named* index below

    sources: Mapped[List["LeadSourceRow"]] = relationship(
        back_populates="lead", cascade="all, delete-orphan", order_by="LeadSourceRow.position"
    )

    __table_args__ = (
        Index("ix_leads_phone_name", "phone", "name_key"),
        # Named, so migrations can add it to an existing table (SQLite needs names for batch alterations)
        Index("uq_leads_crm_id", "crm_id", unique=True),
    )


class LeadSourceRow(Base):
    """One row per channel a lead used. A separate table, not a comma-separated column (1st normal form)."""

    __tablename__ = "lead_sources"

    lead_id: Mapped[str] = mapped_column(ForeignKey("leads.lead_id", ondelete="CASCADE"), primary_key=True)
    source: Mapped[str] = mapped_column(String(20), primary_key=True, index=True)
    position: Mapped[int] = mapped_column(Integer, default=0)
    lead: Mapped[LeadRow] = relationship(back_populates="sources")


class NoteRow(Base):
    __tablename__ = "notes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    lead_id: Mapped[str] = mapped_column(ForeignKey("leads.lead_id", ondelete="CASCADE"), index=True)
    author: Mapped[str] = mapped_column(String(64))
    text: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime)


class FollowUpRow(Base):
    __tablename__ = "followups"

    followup_id: Mapped[str] = mapped_column(String(32), primary_key=True)
    lead_id: Mapped[str] = mapped_column(ForeignKey("leads.lead_id", ondelete="CASCADE"), index=True)
    counsellor: Mapped[str] = mapped_column(String(64))
    due: Mapped[datetime] = mapped_column(DateTime)
    done: Mapped[bool] = mapped_column(Boolean, default=False)

    __table_args__ = (Index("ix_followups_counsellor_due", "counsellor", "done", "due"),)


class UserRow(Base):
    __tablename__ = "users"

    username: Mapped[str] = mapped_column(String(64), primary_key=True)
    full_name: Mapped[str] = mapped_column(String(200))
    role: Mapped[str] = mapped_column(String(20))
    password_hash: Mapped[str] = mapped_column(String(255))


class ImportRun(Base):
    """Audit trail for the ingestion pipeline: what was loaded, when, with what result."""

    __tablename__ = "import_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    file_name: Mapped[str] = mapped_column(String(255))
    file_sha256: Mapped[str] = mapped_column(String(64), index=True)
    fmt: Mapped[str] = mapped_column(String(20))
    started_at: Mapped[datetime] = mapped_column(DateTime)
    rows_read: Mapped[int] = mapped_column(Integer, default=0)
    rows_loaded: Mapped[int] = mapped_column(Integer, default=0)
    rows_merged: Mapped[int] = mapped_column(Integer, default=0)
    rows_rejected: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(20), default="running")


class RejectedRow(Base):
    __tablename__ = "rejected_rows"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    run_id: Mapped[int] = mapped_column(ForeignKey("import_runs.id", ondelete="CASCADE"), index=True)
    line_num: Mapped[int] = mapped_column(Integer)
    reason: Mapped[str] = mapped_column(Text)


class DraftRow(Base):
    """Follow-up drafts written by the assistant; sending requires human approval (Module 08)."""

    __tablename__ = "drafts"

    draft_id: Mapped[str] = mapped_column(String(32), primary_key=True)
    lead_id: Mapped[str] = mapped_column(ForeignKey("leads.lead_id", ondelete="CASCADE"), index=True)
    channel: Mapped[str] = mapped_column(String(20))
    subject: Mapped[str] = mapped_column(String(200))
    body: Mapped[str] = mapped_column(Text)
    requested_by: Mapped[str] = mapped_column(String(64))
    created_at: Mapped[datetime] = mapped_column(DateTime)
    engine: Mapped[str] = mapped_column(String(20), default="offline")
    status: Mapped[str] = mapped_column(String(20), default="pending_approval", index=True)
    decided_by: Mapped[Optional[str]] = mapped_column(String(64))
    decided_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    reason: Mapped[str] = mapped_column(Text, default="")
    sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime)          # Module 09
    external_id: Mapped[Optional[str]] = mapped_column(String(128))       # Module 09


class ProcessedEvent(Base):
    """Webhook event IDs already handled, so a redelivered event isn't processed twice (Module 09)."""

    __tablename__ = "processed_events"

    event_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    received_at: Mapped[datetime] = mapped_column(DateTime)


class AuditRow(Base):
    """Append-only audit log (Module 10). In production, the app's database user should have INSERT and
    SELECT on this table but not UPDATE or DELETE."""

    __tablename__ = "audit_log"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    at: Mapped[datetime] = mapped_column(DateTime, index=True)
    actor: Mapped[str] = mapped_column(String(254), index=True)
    action: Mapped[str] = mapped_column(String(64), index=True)
    target: Mapped[str] = mapped_column(String(128), default="")
    details: Mapped[str] = mapped_column(Text, default="")


# -- conversion between rows and domain objects ------------------------------

def _to_lead(row: LeadRow) -> Lead:
    return Lead(
        lead_id=row.lead_id,
        received_at=row.received_at,
        name=row.name,
        phone=row.phone,
        email=row.email,
        course=row.course,
        sources=[s.source for s in row.sources],
        notes=row.notes or "",
        status=row.status,
        assigned_to=row.assigned_to,
        crm_id=row.crm_id,
    )


def _apply(row: LeadRow, lead: Lead) -> None:
    row.received_at = lead.received_at
    row.name = lead.name
    row.name_key = name_key(lead.name)
    row.phone = lead.phone
    row.email = lead.email
    row.course = lead.course
    row.status = lead.status
    row.assigned_to = lead.assigned_to
    row.notes = lead.notes
    row.crm_id = lead.crm_id
    existing = {s.source for s in row.sources}
    for position, source in enumerate(lead.sources):
        if source not in existing:
            row.sources.append(LeadSourceRow(source=source, position=position))


class SqlRepository:
    def __init__(self, url: str, *, create_tables: bool = False, echo: bool = False):
        # pool_pre_ping: replace connections the database (or a firewall) silently closed
        self.engine = create_engine(url, echo=echo, pool_pre_ping=True, future=True)
        if create_tables:  # tests and quick local use; production uses Alembic migrations
            Base.metadata.create_all(self.engine)

    def session(self) -> Session:
        return Session(self.engine, expire_on_commit=False)

    # -- leads ---------------------------------------------------------------
    def _filtered(self, status=None, source=None, assigned_to=None, search=None):
        query = select(LeadRow)
        if status:
            query = query.where(LeadRow.status == status)
        if assigned_to:
            query = query.where(LeadRow.assigned_to == assigned_to)
        if source:
            query = query.where(LeadRow.sources.any(LeadSourceRow.source == source))
        if search:
            # Parameterized: SQLAlchemy sends `pattern` separately, so input can't change the SQL.
            pattern = f"%{search.casefold()}%"
            query = query.where(
                or_(
                    LeadRow.name_key.like(pattern),
                    func.lower(LeadRow.email).like(pattern),
                    LeadRow.phone.like(pattern),
                    func.lower(LeadRow.course).like(pattern),
                    func.lower(LeadRow.lead_id).like(pattern),
                )
            )
        return query

    def list_leads(self, *, status=None, source=None, assigned_to=None, search=None, offset=0, limit=50):
        base = self._filtered(status, source, assigned_to, search)
        with self.session() as s:
            total = s.scalar(select(func.count()).select_from(base.subquery()))
            rows = s.scalars(
                base.options(selectinload(LeadRow.sources))  # avoid one extra query per lead ("N+1")
                .order_by(LeadRow.received_at.desc(), LeadRow.lead_id)
                .offset(offset)
                .limit(limit)
            ).all()
            return [_to_lead(r) for r in rows], total

    def get_lead(self, lead_id):
        with self.session() as s:
            row = s.get(LeadRow, lead_id, options=[selectinload(LeadRow.sources)])
            return _to_lead(row) if row else None

    def _find_match(self, s: Session, lead: Lead) -> Optional[LeadRow]:
        """Same rules as dedupe.py: same ID, same email, or same phone AND same name."""
        row = s.get(LeadRow, lead.lead_id)
        if row is None and lead.email:
            row = s.scalars(select(LeadRow).where(LeadRow.email == lead.email).limit(1)).first()
        if row is None and lead.phone:
            row = s.scalars(
                select(LeadRow).where(LeadRow.phone == lead.phone, LeadRow.name_key == name_key(lead.name)).limit(1)
            ).first()
        return row

    def add_leads(self, leads):
        added = merged = 0
        with self.session() as s, s.begin():  # one transaction: all or nothing
            for lead in sorted(leads, key=lambda item: item.received_at):
                row = self._find_match(s, lead)
                if row is None:
                    row = LeadRow(lead_id=lead.lead_id)
                    _apply(row, lead)
                    s.add(row)
                    added += 1
                else:
                    current = _to_lead(row)
                    if lead.received_at < current.received_at:  # keep the earliest enquiry's details
                        current.received_at = lead.received_at
                    _merge(current, lead)
                    _apply(row, current)
                    merged += 1
                s.flush()  # make the new row visible to the next lead's match query
        return added, merged

    def update_lead(self, lead):
        with self.session() as s, s.begin():
            row = s.get(LeadRow, lead.lead_id)
            if row is not None:
                _apply(row, lead)

    # -- notes -----------------------------------------------------------------
    def add_note(self, note):
        with self.session() as s, s.begin():
            s.add(NoteRow(lead_id=note.lead_id, author=note.author, text=note.text, created_at=note.created_at))

    def notes_for(self, lead_id):
        with self.session() as s:
            rows = s.scalars(select(NoteRow).where(NoteRow.lead_id == lead_id).order_by(NoteRow.created_at, NoteRow.id))
            return [Note(r.lead_id, r.author, r.text, r.created_at) for r in rows]

    # -- follow-ups ------------------------------------------------------------
    def add_followup(self, lead_id, counsellor, due):
        followup = FollowUp(uuid.uuid4().hex[:12], lead_id, counsellor, due)
        with self.session() as s, s.begin():
            s.add(
                FollowUpRow(
                    followup_id=followup.followup_id, lead_id=lead_id, counsellor=counsellor, due=due, done=False
                )
            )
        return followup

    def followups(self, *, counsellor=None, due_before=None):
        query = select(FollowUpRow)
        if counsellor:
            query = query.where(FollowUpRow.counsellor == counsellor)
        if due_before:
            query = query.where(FollowUpRow.done.is_(False), FollowUpRow.due <= due_before)
        with self.session() as s:
            return [
                FollowUp(r.followup_id, r.lead_id, r.counsellor, r.due, r.done)
                for r in s.scalars(query.order_by(FollowUpRow.due))
            ]

    def complete_followup(self, followup_id):
        with self.session() as s, s.begin():
            row = s.get(FollowUpRow, followup_id)
            if row is None:
                return None
            row.done = True
            return FollowUp(row.followup_id, row.lead_id, row.counsellor, row.due, row.done)

    # -- users -----------------------------------------------------------------
    def get_user(self, username):
        with self.session() as s:
            row = s.get(UserRow, username)
            return User(row.username, row.full_name, row.role, row.password_hash) if row else None

    def save_user(self, user):
        with self.session() as s, s.begin():
            s.merge(UserRow(**user.to_dict()))

    # -- drafts (Module 08) ----------------------------------------------------------
    def save_draft(self, draft):
        with self.session() as s, s.begin():
            s.merge(DraftRow(**draft.to_dict() | {"created_at": draft.created_at, "decided_at": draft.decided_at,
                                                   "sent_at": draft.sent_at}))

    def get_draft(self, draft_id):
        with self.session() as s:
            row = s.get(DraftRow, draft_id)
            return _to_draft(row) if row else None

    def list_drafts(self, *, status=None, lead_id=None):
        query = select(DraftRow)
        if status:
            query = query.where(DraftRow.status == status)
        if lead_id:
            query = query.where(DraftRow.lead_id == lead_id)
        with self.session() as s:
            return [_to_draft(r) for r in s.scalars(query.order_by(DraftRow.created_at))]

    # -- processed events (Module 09) --------------------------------------------------
    def record_event(self, event_id):
        from sqlalchemy.exc import IntegrityError

        try:
            with self.session() as s, s.begin():
                s.add(ProcessedEvent(event_id=event_id, received_at=datetime.now()))
            return True
        except IntegrityError:   # the primary key makes "already seen" atomic, even with concurrent deliveries
            return False


    # -- audit log (Module 10) ------------------------------------------------------------
    def add_audit(self, event):
        with self.session() as s, s.begin():
            s.add(AuditRow(at=event.at, actor=event.actor, action=event.action, target=event.target,
                           details=event.details))

    def list_audit(self, *, actor=None, action=None, limit=100):
        query = select(AuditRow)
        if actor:
            query = query.where(AuditRow.actor == actor)
        if action:
            query = query.where(AuditRow.action.startswith(action))
        with self.session() as s:
            rows = s.scalars(query.order_by(AuditRow.at.desc(), AuditRow.id.desc()).limit(limit))
            return [AuditEvent(r.at, r.actor, r.action, r.target or "", r.details or "") for r in rows]


def _to_draft(row: "DraftRow") -> Draft:
    return Draft(row.draft_id, row.lead_id, row.channel, row.subject, row.body, row.requested_by, row.created_at,
                 row.engine, row.status, row.decided_by, row.decided_at, row.reason or "", row.sent_at, row.external_id)
