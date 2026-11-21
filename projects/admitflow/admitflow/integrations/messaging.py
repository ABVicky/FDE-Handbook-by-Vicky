"""Sending approved drafts: the outbox (added in Module 09).

Only drafts a person has **approved** are ever sent. The outbox picks them up, sends each through
the right channel, and records the provider's message ID. Failures stay `approved` (to be retried)
with the reason recorded; they never become "sent".

Delivery is *at least once*: if the process crashes after the provider accepted a message but
before we recorded it, a retry could send it twice. We narrow that window by marking each draft
immediately after its send, and document it for the client (see Module 09, Lesson 04).
"""
from __future__ import annotations

import logging
import smtplib
from dataclasses import dataclass, field
from datetime import datetime
from email.message import EmailMessage
from typing import Dict, List, Optional, Protocol

from ..observability import metrics

log = logging.getLogger("admitflow.outbox")


class SendError(Exception):
    pass


class Sender(Protocol):
    def send(self, to: str, subject: str, body: str) -> str:
        """Send one message; return the provider's message ID. Raise SendError on failure."""
        ...


class RecordingSender:
    """For tests and local development: keeps messages in memory instead of sending them."""

    def __init__(self, fail_for: Optional[set] = None):
        self.sent: List[Dict[str, str]] = []
        self.fail_for = fail_for or set()

    def send(self, to, subject, body):
        if to in self.fail_for:
            raise SendError(f"provider rejected {to}")
        self.sent.append({"to": to, "subject": subject, "body": body})
        return f"local-{len(self.sent)}"


class SmtpEmailSender:
    """Email through the client's SMTP server (e.g. Google Workspace relay). Credentials from the environment."""

    def __init__(self, host: str, port: int, username: str, password: str, from_addr: str):
        self.host, self.port, self.username, self.password, self.from_addr = host, port, username, password, from_addr

    def send(self, to, subject, body):
        message = EmailMessage()
        message["From"], message["To"], message["Subject"] = self.from_addr, to, subject
        message.set_content(body)
        try:
            with smtplib.SMTP(self.host, self.port, timeout=20) as smtp:
                smtp.starttls()
                smtp.login(self.username, self.password)
                smtp.send_message(message)
        except (smtplib.SMTPException, OSError) as exc:
            raise SendError(str(exc)) from exc
        return message.get("Message-ID") or f"smtp-{datetime.now():%Y%m%d%H%M%S}"


class WhatsAppCloudSender:
    """WhatsApp Business messages over the provider's HTTP API.

    ⚠️ Business messaging platforms restrict *free-form* messages to recent conversations, and require
    pre-approved **templates** to start a conversation. Check the provider's current rules before go-live.
    """

    def __init__(self, base_url: str, token: str, phone_number_id: str, client=None):
        import httpx

        self.url = f"{base_url.rstrip('/')}/{phone_number_id}/messages"
        self.token = token
        self.client = client or httpx.Client(timeout=15)

    def send(self, to, subject, body):
        import httpx

        payload = {"messaging_product": "whatsapp", "to": to.lstrip("+"), "type": "text", "text": {"body": body}}
        try:
            response = self.client.post(self.url, json=payload, headers={"Authorization": f"Bearer {self.token}"})
        except httpx.HTTPError as exc:
            raise SendError(f"network error: {exc}") from exc
        if response.status_code >= 400:
            raise SendError(f"HTTP {response.status_code}: {response.text[:200]}")
        messages = response.json().get("messages") or [{}]
        return messages[0].get("id", "unknown")


@dataclass
class OutboxReport:
    sent: List[str] = field(default_factory=list)
    failed: List[tuple] = field(default_factory=list)     # (draft_id, reason)
    skipped: List[tuple] = field(default_factory=list)    # (draft_id, reason)


def send_approved(repo, senders: Dict[str, Sender]) -> OutboxReport:
    """Send every approved, unsent draft. Safe to run repeatedly (e.g. every minute)."""
    report = OutboxReport()
    for draft in repo.list_drafts(status="approved"):
        lead = repo.get_lead(draft.lead_id)
        to = (lead.email if draft.channel == "email" else lead.phone) if lead else None
        sender = senders.get(draft.channel)
        if not to or sender is None:
            reason = "no address for this channel" if not to else f"no sender configured for {draft.channel}"
            report.skipped.append((draft.draft_id, reason))
            continue
        try:
            external_id = sender.send(to, draft.subject, draft.body)
        except SendError as exc:
            draft.reason = f"send failed: {exc}"
            repo.save_draft(draft)                       # stays approved: retried on the next run
            report.failed.append((draft.draft_id, str(exc)))
            metrics.inc("admitflow_outbox_failed_total", help="Messages the provider rejected or that errored",
                        channel=draft.channel)
            log.warning("draft %s send failed: %s", draft.draft_id, exc)
            continue
        draft.status, draft.external_id, draft.sent_at = "sent", external_id, datetime.now().replace(microsecond=0)
        repo.save_draft(draft)                           # record immediately: keeps the duplicate window small
        report.sent.append(draft.draft_id)
        metrics.inc("admitflow_outbox_sent_total", help="Messages sent", channel=draft.channel)
        log.info("draft %s sent via %s id=%s", draft.draft_id, draft.channel, external_id)
    # How long has the oldest approved-but-unsent message been waiting? Alert on this (runbook: OUTBOX-STUCK).
    waiting = [d.decided_at for d in repo.list_drafts(status="approved") if d.decided_at]
    oldest = (datetime.now() - min(waiting)).total_seconds() / 60 if waiting else 0.0
    metrics.set("admitflow_outbox_oldest_approved_minutes", round(oldest, 1),
                help="Age of the oldest approved draft not yet sent")
    return report
