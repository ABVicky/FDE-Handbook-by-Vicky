"""API tests (Module 04). Skipped automatically if the `api` extras aren't installed."""
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

fastapi = pytest.importorskip("fastapi")
from fastapi.testclient import TestClient  # noqa: E402

from admitflow.api import create_app  # noqa: E402
from admitflow.auth import create_token, hash_password  # noqa: E402
from admitflow.importers import import_file  # noqa: E402
from admitflow.models import User  # noqa: E402
from admitflow.repository import JsonRepository  # noqa: E402

DATA = Path(__file__).resolve().parent.parent / "data"
PASSWORD = "correct horse battery staple"


@pytest.fixture(autouse=True)
def secret(monkeypatch):
    monkeypatch.setenv("ADMITFLOW_SECRET_KEY", "test-secret-key-that-is-long-enough-1234567890")


@pytest.fixture(params=["json", "sql"])
def repo(request, tmp_path):
    if request.param == "sql":
        pytest.importorskip("sqlalchemy")
        from admitflow.db import SqlRepository

        repo = SqlRepository(f"sqlite:///{tmp_path / 'api.db'}", create_tables=True)
    else:
        repo = JsonRepository(tmp_path / "store.json")
    repo.add_leads(import_file(DATA / "leads_sample.csv", "website").leads)
    repo.save_user(User("priya", "Priya Nair", "counsellor", hash_password(PASSWORD)))
    repo.save_user(User("omar", "Omar Haddad", "counsellor", hash_password(PASSWORD)))
    repo.save_user(User("fernandes", "Mr. Fernandes", "admin", hash_password(PASSWORD)))
    return repo


@pytest.fixture
def client(repo):
    return TestClient(create_app(repo))


def auth(username, role="counsellor"):
    return {"Authorization": f"Bearer {create_token(username, role)}"}


# -- authentication ------------------------------------------------------

def test_health_needs_no_login(client):
    assert client.get("/health").json() == {"status": "ok"}


def test_ready_checks_storage(client, repo, monkeypatch):
    assert client.get("/ready").json() == {"status": "ready"}

    def broken(**kwargs):
        raise OSError("database is down")

    monkeypatch.setattr(repo, "list_leads", broken)
    assert client.get("/ready").status_code == 503


def test_login_success_returns_token(client):
    response = client.post("/auth/login", json={"username": "priya", "password": PASSWORD})
    assert response.status_code == 200
    token = response.json()["access_token"]
    assert client.get("/me", headers={"Authorization": f"Bearer {token}"}).json()["username"] == "priya"


@pytest.mark.parametrize("username, password", [("priya", "wrong"), ("nobody", PASSWORD)])
def test_login_failure_gives_same_message(client, username, password):
    response = client.post("/auth/login", json={"username": username, "password": password})
    assert response.status_code == 401
    assert response.json()["error"]["detail"] == "Incorrect username or password"


@pytest.mark.parametrize("headers", [{}, {"Authorization": "Bearer not-a-token"}])
def test_protected_routes_need_valid_token(client, headers):
    assert client.get("/leads", headers=headers).status_code == 401


def test_expired_token_is_rejected(client):
    old = create_token("priya", "counsellor", now=datetime.now() - timedelta(days=2))
    assert client.get("/leads", headers={"Authorization": f"Bearer {old}"}).status_code == 401


# -- leads -----------------------------------------------------------------

def test_list_is_paginated_newest_first(client):
    body = client.get("/leads", params={"page": 2, "page_size": 10}, headers=auth("priya")).json()
    assert body["total"] == 120 and body["page"] == 2 and len(body["items"]) == 10
    first_page = client.get("/leads", params={"page_size": 10}, headers=auth("priya")).json()["items"]
    assert first_page[0]["received_at"] >= first_page[-1]["received_at"]


def test_filters(client):
    body = client.get("/leads", params={"source": "whatsapp"}, headers=auth("priya")).json()
    assert body["total"] == 11
    assert client.get("/leads", params={"status": "nonsense"}, headers=auth("priya")).status_code == 422


def test_page_size_is_capped(client):
    assert client.get("/leads", params={"page_size": 5000}, headers=auth("priya")).status_code == 422


def test_get_missing_lead_is_404(client):
    response = client.get("/leads/ENQ-9999", headers=auth("priya"))
    assert response.status_code == 404
    assert "not found" in response.json()["error"]["detail"]


def test_create_lead_validates_and_normalizes(client):
    response = client.post(
        "/leads",
        json={"name": "  LUCÍA FERNÁNDEZ ", "phone": "(202) 555-0177", "course": "Accounting", "source": "phone"},
        headers=auth("priya"),
    )
    assert response.status_code == 201
    lead = response.json()
    assert lead["name"] == "Lucía Fernández" and lead["phone"] == "+12025550177"


@pytest.mark.parametrize(
    "payload, field",
    [
        ({"name": "123", "source": "phone"}, "name"),
        ({"name": "Omar", "phone": "12", "source": "phone"}, "phone"),
        ({"name": "Omar", "email": "not-an-email", "source": "phone"}, "email"),
        ({"name": "Omar", "source": "fax"}, "source"),
    ],
)
def test_create_lead_rejects_bad_input(client, payload, field):
    response = client.post("/leads", json=payload, headers=auth("priya"))
    assert response.status_code == 422
    assert field in [p["field"] for p in response.json()["error"]["detail"]]


def test_creating_existing_person_merges_and_returns_200(client):
    response = client.post(
        "/leads",
        json={"name": "Grace Patel", "email": "GRACE.PATEL91@example.com", "source": "phone"},
        headers=auth("priya"),
    )
    assert response.status_code == 200
    assert response.json()["lead_id"] == "ENQ-0001"
    assert "phone" in response.json()["sources"]


# -- authorization ---------------------------------------------------------

def test_only_admin_can_assign(client):
    assert client.patch("/leads/ENQ-0001", json={"assigned_to": "priya"}, headers=auth("priya")).status_code == 403
    response = client.patch(
        "/leads/ENQ-0001", json={"assigned_to": "priya"}, headers=auth("fernandes", "admin")
    )
    assert response.status_code == 200 and response.json()["assigned_to"] == "priya"


def test_counsellor_cannot_change_someone_elses_lead(client):
    client.patch("/leads/ENQ-0002", json={"assigned_to": "omar"}, headers=auth("fernandes", "admin"))
    assert client.patch("/leads/ENQ-0002", json={"status": "contacted"}, headers=auth("priya")).status_code == 403
    assert client.patch("/leads/ENQ-0002", json={"status": "contacted"}, headers=auth("omar")).status_code == 200


def test_assign_unknown_counsellor_is_422(client):
    response = client.patch("/leads/ENQ-0001", json={"assigned_to": "ghost"}, headers=auth("fernandes", "admin"))
    assert response.status_code == 422


def test_mine_filter(client):
    client.patch("/leads/ENQ-0003", json={"assigned_to": "priya"}, headers=auth("fernandes", "admin"))
    body = client.get("/leads", params={"mine": True}, headers=auth("priya")).json()
    assert [lead["lead_id"] for lead in body["items"]] == ["ENQ-0003"]


# -- notes, follow-ups, stats ------------------------------------------------

def test_notes_appear_in_history(client):
    assert client.post("/leads/ENQ-0001/notes", json={"text": "Called, interested in evening batch"},
                       headers=auth("priya")).status_code == 201
    detail = client.get("/leads/ENQ-0001", headers=auth("priya")).json()
    assert detail["history"][0]["author"] == "priya"
    assert client.post("/leads/ENQ-0001/notes", json={"text": ""}, headers=auth("priya")).status_code == 422


def test_followup_lifecycle(client):
    due = (datetime.now() + timedelta(hours=2)).isoformat(timespec="minutes")
    created = client.post("/leads/ENQ-0001/followups", json={"due": due}, headers=auth("priya"))
    assert created.status_code == 201
    followup_id = created.json()["followup_id"]

    due_list = client.get("/followups/due", headers=auth("priya")).json()
    assert [f["followup_id"] for f in due_list] == [followup_id]
    assert client.get("/followups/due", headers=auth("omar")).json() == []   # only your own

    done = client.post(f"/followups/{followup_id}/complete", headers=auth("priya"))
    assert done.json()["done"] is True
    assert client.get("/followups/due", headers=auth("priya")).json() == []
    assert client.post("/followups/nope/complete", headers=auth("priya")).status_code == 404


def test_timezone_aware_due_dates_are_converted_to_local_time(client):
    response = client.post("/leads/ENQ-0001/followups", json={"due": "2026-09-20T10:00:00Z"},
                           headers=auth("priya"))
    assert response.status_code == 201
    expected = datetime(2026, 9, 20, 10, 0, tzinfo=timezone.utc).astimezone().replace(tzinfo=None)
    assert response.json()["due"] == expected.isoformat()


def test_stats(client):
    body = client.get("/stats", headers=auth("priya")).json()
    assert body["total"] == 120 and body["unassigned"] == 120
    assert body["by_status"] == {"new": 120}


def test_request_id_header(client):
    response = client.get("/health", headers={"X-Request-ID": "abc123"})
    assert response.headers["X-Request-ID"] == "abc123"
