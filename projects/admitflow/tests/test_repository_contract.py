"""Contract tests: every Repository implementation must behave identically (ADR-001)."""
import os
from datetime import datetime, timedelta
from pathlib import Path

import pytest

from admitflow.importers import import_file
from admitflow.models import Note, User
from admitflow.repository import JsonRepository

DATA = Path(__file__).resolve().parent.parent / "data"
FILES = [("leads_sample.csv", "website"), ("ad_leads.csv", "ads"), ("walkins.csv", "walkins")]


def _sql(tmp_path):
    pytest.importorskip("sqlalchemy")
    from admitflow.db import SqlRepository

    return SqlRepository(f"sqlite:///{tmp_path / 'contract.db'}", create_tables=True)


def _postgres():
    """Only in CI (or when you set TEST_POSTGRES_URL): run the same contract against real PostgreSQL."""
    url = os.environ.get("TEST_POSTGRES_URL")
    if not url:
        pytest.skip("TEST_POSTGRES_URL not set")
    from admitflow.db import Base, SqlRepository

    repo = SqlRepository(url)
    Base.metadata.drop_all(repo.engine)
    Base.metadata.create_all(repo.engine)
    return repo


@pytest.fixture(params=["json", "sql", "postgres"])
def repo(request, tmp_path):
    if request.param == "json":
        repo = JsonRepository(tmp_path / "store.json")
    elif request.param == "sql":
        repo = _sql(tmp_path)
    else:
        repo = _postgres()
    for name, fmt in FILES:
        repo.add_leads(import_file(DATA / name, fmt).leads)
    return repo


def test_same_totals_after_loading_all_files(repo):
    leads, total = repo.list_leads(limit=10_000)
    assert total == 190
    assert sum(len(lead.sources) for lead in leads) == 203


def test_reloading_changes_nothing(repo):
    added, merged = repo.add_leads(import_file(DATA / "ad_leads.csv", "ads").leads)
    assert added == 0 and merged == 60
    assert repo.list_leads()[1] == 190


@pytest.mark.parametrize(
    "filters, expected",
    [
        ({"source": "whatsapp"}, 11),
        ({"source": "walk-in"}, 36),
        ({"search": "nguyễn"}, 4),
        ({"search": "NURSING"}, 35),
        ({"source": "whatsapp", "search": "nurs"}, 4),
        ({"status": "new"}, 190),
        ({"status": "enrolled"}, 0),
    ],
)
def test_filters(repo, filters, expected):
    assert repo.list_leads(**filters)[1] == expected


def test_pagination_is_stable_and_newest_first(repo):
    first, _ = repo.list_leads(offset=0, limit=50)
    second, _ = repo.list_leads(offset=50, limit=50)
    assert not {l.lead_id for l in first} & {l.lead_id for l in second}
    times = [l.received_at for l in first + second]
    assert times == sorted(times, reverse=True)


def test_merged_lead_keeps_all_channels(repo):
    (lead,) = [l for l in repo.list_leads(search="daniel okoye", limit=5)[0] if "walk-in" in l.sources]
    assert lead.sources == ["website", "ad", "walk-in"]


def test_update_and_assignment(repo):
    repo.save_user(User("priya", "Priya Nair", "counsellor", "x"))
    lead = repo.get_lead("ENQ-0001")
    lead.status, lead.assigned_to = "contacted", "priya"
    repo.update_lead(lead)
    again = repo.get_lead("ENQ-0001")
    assert (again.status, again.assigned_to) == ("contacted", "priya")
    assert repo.list_leads(assigned_to="priya")[1] == 1
    assert repo.get_lead("NOPE") is None


def test_notes_in_order(repo):
    t = datetime(2026, 9, 20, 10, 0)
    repo.add_note(Note("ENQ-0001", "priya", "second", t + timedelta(minutes=5)))
    repo.add_note(Note("ENQ-0001", "priya", "first", t))
    assert [n.text for n in repo.notes_for("ENQ-0001")] == ["first", "second"]


def test_followups(repo):
    now = datetime(2026, 9, 20, 9, 0)
    soon = repo.add_followup("ENQ-0001", "priya", now + timedelta(hours=1))
    repo.add_followup("ENQ-0002", "priya", now + timedelta(days=3))
    repo.add_followup("ENQ-0003", "omar", now + timedelta(hours=1))
    due = repo.followups(counsellor="priya", due_before=now + timedelta(hours=24))
    assert [f.followup_id for f in due] == [soon.followup_id]
    assert repo.complete_followup(soon.followup_id).done is True
    assert repo.followups(counsellor="priya", due_before=now + timedelta(hours=24)) == []
    assert repo.complete_followup("missing") is None


def test_users(repo):
    repo.save_user(User("priya", "Priya", "counsellor", "hash1"))
    repo.save_user(User("priya", "Priya Nair", "admin", "hash2"))  # update, not duplicate
    assert repo.get_user("priya") == User("priya", "Priya Nair", "admin", "hash2")
    assert repo.get_user("ghost") is None


def test_drafts(repo):
    from admitflow.models import Draft

    draft = Draft("d1", "ENQ-0001", "email", "Hi", "Hello Grace", "priya", datetime(2026, 9, 20, 10, 0))
    repo.save_draft(draft)
    repo.save_draft(Draft("d2", "ENQ-0002", "whatsapp", "Hi", "Hello", "omar", datetime(2026, 9, 20, 11, 0)))
    assert [d.draft_id for d in repo.list_drafts(status="pending_approval")] == ["d1", "d2"]
    draft.status, draft.decided_by, draft.decided_at = "approved", "priya", datetime(2026, 9, 20, 12, 0)
    repo.save_draft(draft)                                     # update, not duplicate
    assert repo.get_draft("d1") == draft
    assert [d.draft_id for d in repo.list_drafts(status="pending_approval")] == ["d2"]
    assert [d.draft_id for d in repo.list_drafts(lead_id="ENQ-0001")] == ["d1"]
    assert repo.get_draft("missing") is None


def test_events_are_recorded_once(repo):
    assert repo.record_event("evt_1") is True
    assert repo.record_event("evt_1") is False
    assert repo.record_event("evt_2") is True


def test_crm_id_round_trip(repo):
    lead = repo.get_lead("ENQ-0001")
    lead.crm_id = "crm-42"
    repo.update_lead(lead)
    assert repo.get_lead("ENQ-0001").crm_id == "crm-42"


def test_audit_log(repo):
    from admitflow.models import AuditEvent

    base = datetime(2026, 9, 20, 9, 0)
    repo.add_audit(AuditEvent(base, "priya", "lead.status", "ENQ-0001", "new -> contacted"))
    repo.add_audit(AuditEvent(base + timedelta(minutes=1), "fernandes", "lead.assign", "ENQ-0002"))
    repo.add_audit(AuditEvent(base + timedelta(minutes=2), "priya", "draft.approve", "d1"))
    assert [e.action for e in repo.list_audit()] == ["draft.approve", "lead.assign", "lead.status"]
    assert [e.action for e in repo.list_audit(actor="priya")] == ["draft.approve", "lead.status"]
    assert [e.target for e in repo.list_audit(action="lead.")] == ["ENQ-0002", "ENQ-0001"]
    assert len(repo.list_audit(limit=1)) == 1
