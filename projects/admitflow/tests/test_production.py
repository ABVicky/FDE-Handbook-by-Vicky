"""Production hardening (Module 10): privacy, rate limits, headers, metrics, audit, backups."""
import logging
import os
from datetime import datetime, timedelta
from pathlib import Path
from types import SimpleNamespace

import pytest

from admitflow.importers import import_file
from admitflow.models import AuditEvent, Draft, User
from admitflow.observability import Registry, metrics
from admitflow.privacy import RedactingFilter, redact
from admitflow.repository import JsonRepository
from admitflow.security import RateLimiter

DATA = Path(__file__).resolve().parent.parent / "data"


# -- privacy ----------------------------------------------------------------------------------------

@pytest.mark.parametrize(
    "text, expected",
    [
        ("Call +1 202-555-0141 or grace.patel@example.com", "Call [phone] or g***@example.com"),
        ("her number is (202) 555 0141.", "her number is [phone]."),
        ("Intake 2026, fee 1,800, ENQ-0001", "Intake 2026, fee 1,800, ENQ-0001"),     # not phone numbers
        ("", ""),
    ],
)
def test_redact(text, expected):
    assert redact(text) == expected


def test_log_records_are_redacted(caplog):
    logger = logging.getLogger("admitflow.test")
    handler = logging.Handler()
    seen = []
    handler.emit = lambda record: seen.append(record.getMessage())
    handler.addFilter(RedactingFilter())
    logger.addHandler(handler)
    try:
        logger.warning("could not reach %s at %s", "grace@example.com", "+1 202 555 0141")
    finally:
        logger.removeHandler(handler)
    assert seen == ["could not reach g***@example.com at [phone]"]


def test_drafter_sends_minimal_personal_data():
    pytest.importorskip("pydantic")
    from admitflow.llm import ClaudeDrafter
    from admitflow.models import Lead, Note

    calls = []
    client = SimpleNamespace(beta=SimpleNamespace(messages=SimpleNamespace(
        parse=lambda **kw: calls.append(kw) or SimpleNamespace(stop_reason="end_turn", parsed_output=SimpleNamespace(
            channel="email", subject="s", body="b")))))
    lead = Lead("ENQ-1", datetime(2026, 9, 1), "Grace Patel", "+12025550141", "grace@example.com", "Accounting", ["website"])
    note = Note("ENQ-1", "priya", "She asked us to use grace.alt@example.com or 202 555 0199", datetime(2026, 9, 2))
    ClaudeDrafter(client=client).draft(lead, [note], [])
    content = calls[0]["messages"][0]["content"]
    assert "Grace" in content and "Patel" not in content
    assert "grace.alt@example.com" not in content and "555 0199" not in content and "+12025550141" not in content


# -- rate limiting --------------------------------------------------------------------------------------

def test_token_bucket():
    limiter = RateLimiter(rate_per_minute=60, burst=3)       # one token per second, three in reserve
    assert [limiter.allow("ip", now=0)[0] for _ in range(4)] == [True, True, True, False]
    allowed, wait = limiter.allow("ip", now=0.5)
    assert not allowed and 0 < wait <= 1
    assert limiter.allow("ip", now=1.6)[0]                   # refilled
    assert limiter.allow("other-ip", now=0)[0]               # separate bucket per key


# -- API ---------------------------------------------------------------------------------------------------

@pytest.fixture
def api(tmp_path, monkeypatch):
    pytest.importorskip("fastapi")
    from fastapi.testclient import TestClient

    from admitflow.api import create_app
    from admitflow.assistant import build_assistant
    from admitflow.auth import create_token, hash_password

    monkeypatch.setenv("ADMITFLOW_SECRET_KEY", "test-secret-key-that-is-long-enough-1234567890")
    monkeypatch.setenv("ADMITFLOW_METRICS_TOKEN", "metrics-token-123")
    repo = JsonRepository(tmp_path / "s.json")
    repo.add_leads(import_file(DATA / "leads_sample.csv", "website").leads)
    repo.save_user(User("priya", "Priya", "counsellor", hash_password("a-long-password-1")))
    repo.save_user(User("fernandes", "Mr. Fernandes", "admin", "x"))
    client = TestClient(create_app(repo, assistant=build_assistant(str(DATA / "course_docs"))))

    def auth(user, role="counsellor"):
        return {"Authorization": f"Bearer {create_token(user, role)}"}

    return client, repo, auth


def test_security_headers(api):
    client, _, _ = api
    headers = client.get("/health").headers
    assert headers["X-Content-Type-Options"] == "nosniff"
    assert headers["Cache-Control"] == "no-store"
    assert "frame-ancestors 'none'" in headers["Content-Security-Policy"]


def test_public_endpoint_is_rate_limited(api):
    client, _, _ = api
    statuses = [client.post("/public/assistant/ask", json={"question": "fees?"}).status_code for _ in range(12)]
    assert statuses[:10] == [200] * 10 and statuses[-1] == 429
    limited = client.post("/public/assistant/ask", json={"question": "fees?"})
    assert int(limited.headers["Retry-After"]) >= 1
    assert client.get("/health").status_code == 200           # non-public routes unaffected


def test_login_is_rate_limited_and_audited(api):
    client, repo, _ = api
    statuses = [client.post("/auth/login", json={"username": "priya", "password": "wrong"}).status_code for _ in range(6)]
    assert statuses == [401] * 5 + [429]
    actions = [e.action for e in repo.list_audit(actor="priya")]
    assert actions.count("auth.login.failed") == 5 and "auth.login.rate_limited" in actions


def test_changes_are_audited(api):
    client, repo, auth = api
    client.patch("/leads/ENQ-0001", json={"assigned_to": "priya"}, headers=auth("fernandes", "admin"))
    client.patch("/leads/ENQ-0001", json={"status": "contacted"}, headers=auth("priya"))
    draft = client.post("/leads/ENQ-0001/drafts", headers=auth("priya")).json()
    client.post(f"/drafts/{draft['draft_id']}/approve", headers=auth("priya"))
    events = {(e.actor, e.action, e.target) for e in repo.list_audit()}
    assert ("fernandes", "lead.assign", "ENQ-0001") in events
    assert ("priya", "lead.status", "ENQ-0001") in events
    assert ("priya", "draft.approve", draft["draft_id"]) in events
    body = client.get("/audit", params={"action": "lead."}, headers=auth("fernandes", "admin")).json()
    assert {e["action"] for e in body} == {"lead.assign", "lead.status"}
    assert client.get("/audit", headers=auth("priya")).status_code == 403


def test_metrics_endpoint(api, monkeypatch):
    client, _, auth = api
    client.get("/leads", headers=auth("priya"))
    client.post("/public/assistant/ask", json={"question": "Where is the North campus?"})
    assert client.get("/metrics").status_code == 401
    text = client.get("/metrics", headers={"Authorization": "Bearer metrics-token-123"}).text
    assert 'admitflow_http_requests_total{method="GET",route="/leads",status="200"}' in text
    assert 'admitflow_http_request_seconds_bucket{route="/leads",le="+Inf"}' in text
    assert "admitflow_assistant_questions_total" in text
    monkeypatch.delenv("ADMITFLOW_METRICS_TOKEN")
    assert client.get("/metrics").status_code == 503


# -- metrics registry and outbox gauges ---------------------------------------------------------------------

def test_registry_renders_prometheus_format():
    registry = Registry()
    registry.inc("jobs_total", help="Jobs", kind="import")
    registry.set("queue_age_minutes", 12.5)
    registry.observe("latency_seconds", 0.03)
    text = registry.render()
    assert 'jobs_total{kind="import"} 1' in text and "queue_age_minutes 12.5" in text
    assert 'latency_seconds_bucket{le="0.05"} 1' in text and 'latency_seconds_bucket{le="0.025"} 0' in text


def test_outbox_reports_stuck_messages(tmp_path):
    from admitflow.integrations.messaging import RecordingSender, send_approved

    repo = JsonRepository(tmp_path / "s.json")
    repo.add_leads(import_file(DATA / "leads_sample.csv", "website").leads)
    old = Draft("d1", "ENQ-0001", "email", "s", "b", "priya", datetime.now() - timedelta(hours=3),
                status="approved", decided_at=datetime.now() - timedelta(hours=3))
    repo.save_draft(old)
    send_approved(repo, {"email": RecordingSender(fail_for={"grace.patel91@example.com"})})
    assert metrics.value("admitflow_outbox_oldest_approved_minutes") >= 179
    assert metrics.value("admitflow_outbox_failed_total", channel="email") >= 1
    send_approved(repo, {"email": RecordingSender()})
    assert metrics.value("admitflow_outbox_oldest_approved_minutes") == 0


# -- backups ------------------------------------------------------------------------------------------------

def test_backup_and_verify(tmp_path, monkeypatch, capsys):
    pytest.importorskip("sqlalchemy")
    from admitflow.cli import main
    from admitflow.db import SqlRepository

    url = f"sqlite:///{tmp_path / 'live.db'}"
    repo = SqlRepository(url, create_tables=True)
    repo.add_leads(import_file(DATA / "walkins.csv", "walkins").leads)
    repo.add_audit(AuditEvent(datetime.now(), "test", "backup.test"))
    monkeypatch.setenv("DATABASE_URL", url)
    assert main(["backup", "--to", str(tmp_path / "copy.db")]) == 0
    out = capsys.readouterr().out
    assert "integrity: ok" in out and "leads            25" in out
    restored = SqlRepository(f"sqlite:///{tmp_path / 'copy.db'}")
    assert restored.list_leads()[1] == 25                     # the restore drill: the app can read the copy
    monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg://x@y/z")
    assert main(["backup", "--to", str(tmp_path / "pg.db")]) == 2
