"""HTTP routes. Each function is small: validate (Pydantic) → authorize → call the repository."""
from __future__ import annotations

import logging
import uuid
from collections import Counter
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, Request, Response, status

from ..auth import create_token, verify_password
from ..models import AuditEvent, Lead, Note, User
from ..observability import metrics
from ..repository import Repository
from .deps import current_user, get_repo, require_admin
from .schemas import (
    FollowUpIn,
    FollowUpOut,
    LeadCreate,
    LeadDetail,
    LeadOut,
    LeadPage,
    LeadUpdate,
    LoginIn,
    NoteIn,
    AskIn,
    AskOut,
    GoogleLoginIn,
    WebFormIn,
    DraftDecision,
    DraftOut,
    NoteOut,
    PriorityLead,
    ScoreOut,
    Stats,
    Status,
    TokenOut,
)

log = logging.getLogger("admitflow.api")
router = APIRouter()


def audit(repo: Repository, actor: str, action: str, target: str = "", details: str = "") -> None:
    repo.add_audit(AuditEvent(datetime.now().replace(microsecond=0), actor, action, target, details[:500]))


def _get_lead_or_404(repo: Repository, lead_id: str) -> Lead:
    lead = repo.get_lead(lead_id)
    if lead is None:
        raise HTTPException(status_code=404, detail=f"Lead {lead_id} not found")
    return lead


def _notify_assignment(lead_id: str, counsellor: str) -> None:
    # Module 09 replaces this with a real email / WhatsApp message.
    log.info("notify %s: lead %s assigned to you", counsellor, lead_id)


@router.get("/health", tags=["ops"])
def health() -> dict:
    """Liveness: the process is up. Never touches the database, so it stays cheap."""
    return {"status": "ok"}


@router.get("/ready", tags=["ops"])
def ready(repo: Repository = Depends(get_repo)) -> dict:
    """Readiness: can we serve real requests? Load balancers send traffic only when this is 200."""
    try:
        repo.list_leads(limit=1)
    except Exception as exc:  # any storage failure means "not ready"
        log.error("readiness check failed: %s", exc)
        raise HTTPException(status_code=503, detail="storage unavailable") from None
    return {"status": "ready"}


@router.post("/auth/login", response_model=TokenOut, tags=["auth"])
def login(body: LoginIn, request: Request, repo: Repository = Depends(get_repo)) -> TokenOut:
    allowed, wait = request.app.state.login_limiter.allow(body.username.lower())   # slows password guessing
    if not allowed:
        audit(repo, body.username, "auth.login.rate_limited")
        raise HTTPException(status_code=429, detail="Too many login attempts. Try again shortly.",
                            headers={"Retry-After": str(int(wait) + 1)})
    user = repo.get_user(body.username)
    # Same message whether the user exists or not: don't help attackers guess usernames.
    if user is None or not verify_password(body.password, user.password_hash):
        audit(repo, body.username, "auth.login.failed")
        metrics.inc("admitflow_login_failures_total", help="Failed password logins")
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    audit(repo, user.username, "auth.login")
    return TokenOut(
        access_token=create_token(user.username, user.role),
        username=user.username,
        full_name=user.full_name,
        role=user.role,
    )


@router.get("/me", tags=["auth"])
def me(user: User = Depends(current_user)) -> dict:
    return {"username": user.username, "full_name": user.full_name, "role": user.role}


@router.get("/leads", response_model=LeadPage, tags=["leads"])
def list_leads(
    status_: Optional[Status] = Query(default=None, alias="status"),
    source: Optional[str] = None,
    search: Optional[str] = Query(default=None, max_length=100),
    mine: bool = False,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=25, ge=1, le=100),
    user: User = Depends(current_user),
    repo: Repository = Depends(get_repo),
) -> LeadPage:
    items, total = repo.list_leads(
        status=status_,
        source=source,
        search=search,
        assigned_to=user.username if mine else None,
        offset=(page - 1) * page_size,
        limit=page_size,
    )
    return LeadPage(items=items, total=total, page=page, page_size=page_size)


@router.post("/leads", response_model=LeadOut, status_code=status.HTTP_201_CREATED, tags=["leads"])
def create_lead(
    body: LeadCreate,
    response: Response,
    user: User = Depends(current_user),
    repo: Repository = Depends(get_repo),
) -> Lead:
    """201 Created for a new person. If they're already in AdmitFlow (same email, or same
    phone and name), the enquiry is merged into the existing record and we return that
    record with 200 OK, so reception can see the history straight away."""
    lead = Lead(
        lead_id=f"{body.source.upper().replace('-', '')}-{uuid.uuid4().hex[:8]}",
        received_at=datetime.now().replace(microsecond=0),
        name=body.name,
        phone=body.phone,
        email=body.email,
        course=body.course,
        sources=[body.source],
    )
    added, merged = repo.add_leads([lead])
    if merged:
        response.status_code = status.HTTP_200_OK
        matches, _ = repo.list_leads(search=lead.email or lead.phone, limit=1)
        return matches[0] if matches else lead
    return lead


def _scorer(request: Request):
    scorer = getattr(request.app.state, "scorer", None)
    if scorer is None:
        raise HTTPException(status_code=503, detail="Lead scoring model not available")
    return scorer


@router.get("/leads/priority", response_model=list[PriorityLead], tags=["scoring"])
def priority_queue(
    request: Request,
    limit: int = Query(default=20, ge=1, le=100),
    user: User = Depends(current_user),
    repo: Repository = Depends(get_repo),
):
    """Who to call next: new leads waiting over 24 hours first (speed matters most), then by score."""
    scorer = _scorer(request)
    leads, _ = repo.list_leads(status="new", limit=10_000)
    now = datetime.now()
    rows = []
    for lead in leads:
        if lead.assigned_to not in (None, user.username):
            continue
        score = scorer.score(lead)
        waiting = (now - lead.received_at).total_seconds() / 3600
        rows.append((waiting > 24, score.probability, lead, score, waiting))
    rows.sort(key=lambda r: (r[0], r[1]), reverse=True)
    return [
        PriorityLead(lead_id=lead.lead_id, name=lead.name, course=lead.course, sources=lead.sources,
                     hours_waiting=round(waiting, 1), score=score.probability, band=score.band, factors=score.factors)
        for _, _, lead, score, waiting in rows[:limit]
    ]


@router.get("/leads/{lead_id}/score", response_model=ScoreOut, tags=["scoring"])
def lead_score(lead_id: str, request: Request, user: User = Depends(current_user), repo: Repository = Depends(get_repo)):
    scorer = _scorer(request)
    score = scorer.score(_get_lead_or_404(repo, lead_id))
    return ScoreOut(lead_id=lead_id, probability=score.probability, band=score.band, factors=score.factors,
                    model_version=score.model_version)


@router.get("/leads/{lead_id}", response_model=LeadDetail, tags=["leads"])
def get_lead(lead_id: str, user: User = Depends(current_user), repo: Repository = Depends(get_repo)) -> dict:
    lead = _get_lead_or_404(repo, lead_id)
    history = [NoteOut.model_validate(n) for n in repo.notes_for(lead_id)]
    return {**LeadOut.model_validate(lead).model_dump(), "history": history}


@router.patch("/leads/{lead_id}", response_model=LeadOut, tags=["leads"])
def update_lead(
    lead_id: str,
    body: LeadUpdate,
    background: BackgroundTasks,
    user: User = Depends(current_user),
    repo: Repository = Depends(get_repo),
) -> Lead:
    lead = _get_lead_or_404(repo, lead_id)
    changes = body.model_dump(exclude_unset=True)

    if "assigned_to" in changes and user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can assign leads")
    if lead.assigned_to not in (None, user.username) and user.role != "admin":
        raise HTTPException(status_code=403, detail="This lead is assigned to another counsellor")
    if changes.get("assigned_to") and repo.get_user(changes["assigned_to"]) is None:
        raise HTTPException(status_code=422, detail=f"Unknown counsellor {changes['assigned_to']}")

    for field_name, value in changes.items():
        if getattr(lead, field_name) != value:
            audit(repo, user.username, f"lead.{'assign' if field_name == 'assigned_to' else field_name}", lead.lead_id,
                  f"{getattr(lead, field_name)} -> {value}")
        setattr(lead, field_name, value)
    repo.update_lead(lead)
    if changes.get("assigned_to"):
        background.add_task(_notify_assignment, lead.lead_id, changes["assigned_to"])
    return lead


@router.post("/leads/{lead_id}/notes", response_model=NoteOut, status_code=201, tags=["leads"])
def add_note(lead_id: str, body: NoteIn, user: User = Depends(current_user), repo: Repository = Depends(get_repo)) -> Note:
    _get_lead_or_404(repo, lead_id)
    note = Note(lead_id, user.username, body.text, datetime.now().replace(microsecond=0))
    repo.add_note(note)
    return note


@router.post("/leads/{lead_id}/followups", response_model=FollowUpOut, status_code=201, tags=["follow-ups"])
def schedule_followup(
    lead_id: str, body: FollowUpIn, user: User = Depends(current_user), repo: Repository = Depends(get_repo)
):
    _get_lead_or_404(repo, lead_id)
    # All AdmitFlow times are naive *institute local time* (docs/adr/002-local-time.md).
    # Convert times sent with an offset (e.g. "...Z" or "+05:30") instead of just dropping the offset.
    due = body.due.astimezone().replace(tzinfo=None) if body.due.tzinfo else body.due
    return repo.add_followup(lead_id, user.username, due)


@router.get("/followups/due", response_model=list[FollowUpOut], tags=["follow-ups"])
def due_followups(
    within_hours: int = Query(default=24, ge=0, le=24 * 14),
    user: User = Depends(current_user),
    repo: Repository = Depends(get_repo),
):
    return repo.followups(counsellor=user.username, due_before=datetime.now() + timedelta(hours=within_hours))


@router.post("/followups/{followup_id}/complete", response_model=FollowUpOut, tags=["follow-ups"])
def complete_followup(followup_id: str, user: User = Depends(current_user), repo: Repository = Depends(get_repo)):
    followup = repo.complete_followup(followup_id)
    if followup is None:
        raise HTTPException(status_code=404, detail="Follow-up not found")
    return followup


@router.get("/stats", response_model=Stats, tags=["reports"])
def stats(user: User = Depends(current_user), repo: Repository = Depends(get_repo)) -> Stats:
    leads, total = repo.list_leads(limit=1_000_000)
    return Stats(
        total=total,
        by_status=dict(Counter(lead.status for lead in leads)),
        by_source=dict(Counter(s for lead in leads for s in lead.sources)),
        unassigned=sum(1 for lead in leads if not lead.assigned_to),
    )


# -- course assistant (Module 08) -------------------------------------------------------------

def _assistant(request: Request):
    assistant = getattr(request.app.state, "assistant", None)
    if assistant is None:
        raise HTTPException(status_code=503, detail="Course assistant not available")
    return assistant


public = APIRouter(prefix="/public", tags=["public"])


@public.post("/assistant/ask", response_model=AskOut)
def ask_assistant(body: AskIn, request: Request) -> AskOut:
    """Deliberately public (the website chat widget). Rate limiting is added in Module 10."""
    answer, hits = _assistant(request).ask(body.question)
    by_id = {h.chunk.chunk_id: h.chunk for h in hits}
    citations = [{"chunk_id": c, "title": by_id[c].title, "section": by_id[c].section} for c in answer.citations if c in by_id]
    metrics.inc("admitflow_assistant_questions_total", help="Questions asked", answered=answer.answered,
                engine=answer.engine)
    log.info("assistant answered=%s citations=%s engine=%s", answer.answered, answer.citations, answer.engine)
    return AskOut(answer=answer.text, answered=answer.answered, citations=citations)


def _can_act_on(user: User, lead: Lead) -> bool:
    return user.role == "admin" or lead.assigned_to in (None, user.username)


@router.post("/leads/{lead_id}/drafts", response_model=DraftOut, status_code=201, tags=["assistant"])
def create_draft(lead_id: str, request: Request, user: User = Depends(current_user), repo: Repository = Depends(get_repo)):
    lead = _get_lead_or_404(repo, lead_id)
    if not _can_act_on(user, lead):
        raise HTTPException(status_code=403, detail="This lead is assigned to another counsellor")
    draft = _assistant(request).draft_followup(lead, repo.notes_for(lead_id), requested_by=user.username)
    repo.save_draft(draft)
    return draft


@router.get("/drafts", response_model=list[DraftOut], tags=["assistant"])
def list_drafts(status_: Optional[str] = Query(default="pending_approval", alias="status"),
                user: User = Depends(current_user), repo: Repository = Depends(get_repo)):
    drafts = repo.list_drafts(status=status_ or None)
    if user.role != "admin":
        drafts = [d for d in drafts if _can_act_on(user, repo.get_lead(d.lead_id))]
    return drafts


def _decide(draft_id: str, new_status: str, reason: str, user: User, repo: Repository):
    draft = repo.get_draft(draft_id)
    if draft is None:
        raise HTTPException(status_code=404, detail="Draft not found")
    if not _can_act_on(user, _get_lead_or_404(repo, draft.lead_id)):
        raise HTTPException(status_code=403, detail="This lead is assigned to another counsellor")
    if draft.status != "pending_approval":
        raise HTTPException(status_code=409, detail=f"Draft is already {draft.status}")
    draft.status, draft.decided_by, draft.reason = new_status, user.username, reason
    draft.decided_at = datetime.now().replace(microsecond=0)
    repo.save_draft(draft)
    audit(repo, user.username, f"draft.{'approve' if new_status == 'approved' else 'reject'}", draft.draft_id,
          f"lead {draft.lead_id}")
    return draft


@router.post("/drafts/{draft_id}/approve", response_model=DraftOut, tags=["assistant"])
def approve_draft(draft_id: str, body: DraftDecision = DraftDecision(),
                  user: User = Depends(current_user), repo: Repository = Depends(get_repo)):
    """A person approves the exact text. Module 09 sends approved drafts; nothing sends unapproved ones."""
    return _decide(draft_id, "approved", body.reason, user, repo)


@router.post("/drafts/{draft_id}/reject", response_model=DraftOut, tags=["assistant"])
def reject_draft(draft_id: str, body: DraftDecision = DraftDecision(),
                 user: User = Depends(current_user), repo: Repository = Depends(get_repo)):
    return _decide(draft_id, "rejected", body.reason, user, repo)


# -- integrations (Module 09) ------------------------------------------------------------------

@public.post("/webhooks/website-form", status_code=200)
async def website_form_webhook(request: Request) -> dict:
    """Signed webhook from the website. Verify → validate → upsert (idempotent) → record the event."""
    import json
    import os
    import re

    from pydantic import ValidationError

    from ..integrations.webhooks import WebhookError, verify
    from ..normalize import normalize_course, normalize_email, normalize_name, normalize_phone

    secret = os.environ.get("ADMITFLOW_WEBHOOK_SECRET")
    if not secret:
        raise HTTPException(status_code=503, detail="Webhook not configured")
    body = await request.body()
    try:
        verify(secret, request.headers.get("X-AdmitFlow-Timestamp"), body, request.headers.get("X-AdmitFlow-Signature"))
    except WebhookError as exc:
        log.warning("rejected webhook: %s", exc)
        raise HTTPException(status_code=401, detail="Invalid signature") from None
    event_id = request.headers.get("X-AdmitFlow-Event-Id", "")
    if not re.fullmatch(r"[A-Za-z0-9_-]{8,64}", event_id):
        raise HTTPException(status_code=400, detail="Missing or invalid X-AdmitFlow-Event-Id")
    try:
        form = WebFormIn.model_validate(json.loads(body))
    except (ValueError, ValidationError):
        raise HTTPException(status_code=422, detail="Invalid form payload") from None

    repo: Repository = request.app.state.repo
    lead = Lead(
        lead_id=f"WEB-{event_id[:24]}",          # derived from the event: a redelivery maps to the same lead
        received_at=datetime.now().replace(microsecond=0),
        name=normalize_name(form.name),
        phone=normalize_phone(form.phone),
        email=normalize_email(form.email),
        course=normalize_course(form.course),
        sources=["website"],
        notes=form.message[:2000],
    )
    if not any(ch.isalpha() for ch in lead.name) or not (lead.email or lead.phone):
        raise HTTPException(status_code=422, detail="A name and an email or phone number are required")
    added, merged = repo.add_leads([lead])
    first_time = repo.record_event(event_id)
    outcome = "duplicate" if not first_time else ("created" if added else "merged")
    if first_time:
        audit(repo, "website", f"webhook.{outcome}", lead.lead_id, f"event {event_id}")
    log.info("webhook event=%s outcome=%s", event_id, outcome)
    return {"status": outcome}


@router.post("/auth/google", response_model=TokenOut, tags=["auth"])
def google_login(body: GoogleLoginIn, request: Request, repo: Repository = Depends(get_repo)) -> TokenOut:
    """Exchange a Google ID token for an AdmitFlow session. Users must already be provisioned (username = email)."""
    from ..integrations.oidc import SsoError, sso_settings, verify_google_id_token

    settings = sso_settings()
    if settings is None:
        raise HTTPException(status_code=503, detail="Google sign-in not configured")
    try:
        identity = verify_google_id_token(body.id_token, *settings, jwks_client=getattr(request.app.state, "google_jwks", None))
    except SsoError as exc:
        log.warning("google login rejected: %s", exc)
        raise HTTPException(status_code=401, detail="Google sign-in failed") from None
    user = repo.get_user(identity.email)
    if user is None:
        audit(repo, identity.email, "auth.google.not_provisioned")
        raise HTTPException(status_code=403, detail="Your account isn't set up in AdmitFlow. Ask an administrator.")
    audit(repo, user.username, "auth.google")
    return TokenOut(access_token=create_token(user.username, user.role), username=user.username,
                    full_name=user.full_name, role=user.role)


# -- operations (Module 10) -----------------------------------------------------------------------

@router.get("/metrics", tags=["ops"], include_in_schema=False)
def metrics_endpoint(request: Request):
    """Prometheus scrape endpoint. Requires `Authorization: Bearer $ADMITFLOW_METRICS_TOKEN`."""
    import hmac
    import os

    from fastapi.responses import PlainTextResponse

    token = os.environ.get("ADMITFLOW_METRICS_TOKEN")
    if not token:
        raise HTTPException(status_code=503, detail="Metrics not configured")
    supplied = request.headers.get("Authorization", "")
    if not hmac.compare_digest(supplied, f"Bearer {token}"):
        raise HTTPException(status_code=401, detail="Metrics token required")
    return PlainTextResponse(metrics.render(), media_type="text/plain; version=0.0.4")


@router.get("/audit", tags=["ops"])
def audit_log(actor: Optional[str] = None, action: Optional[str] = None,
              limit: int = Query(default=100, ge=1, le=1000),
              user: User = Depends(require_admin), repo: Repository = Depends(get_repo)) -> list:
    return [event.to_dict() for event in repo.list_audit(actor=actor, action=action, limit=limit)]
