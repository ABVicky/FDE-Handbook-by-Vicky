from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient

import app as service

AUTH = {"Authorization": "Bearer dev-token"}


@pytest.fixture(autouse=True)
def empty_db():
    service.DB.clear()


@pytest.fixture
def client():
    return TestClient(service.app)


def make(client, lead_id, hours_from_now):
    due = (datetime.now(timezone.utc) + timedelta(hours=hours_from_now)).isoformat(timespec="minutes")
    return client.post("/followups", json={"lead_id": lead_id, "due": due, "who": "priya"}, headers=AUTH)


def test_create_returns_201(client):
    assert make(client, "ENQ-1", 2).status_code == 201


def test_requires_token(client):
    assert client.get("/followups").status_code == 401


def test_first_page_contains_earliest(client):
    for n in range(12):
        make(client, f"ENQ-{n}", n + 1)
    first = client.get("/followups", params={"page": 1, "size": 10}, headers=AUTH).json()
    assert len(first) == 10 and first[0]["lead_id"] == "ENQ-0"
    second = client.get("/followups", params={"page": 2, "size": 10}, headers=AUTH).json()
    assert [r["lead_id"] for r in second] == ["ENQ-10", "ENQ-11"]


def test_overdue(client):
    make(client, "late", -3)
    make(client, "later", 5)
    response = client.get("/followups/overdue", headers=AUTH)
    assert response.status_code == 200
    assert [r["lead_id"] for r in response.json()] == ["late"]


def test_delete_requires_token(client):
    make(client, "ENQ-1", 1)
    assert client.delete("/followups/1").status_code == 401
    assert client.delete("/followups/1", headers=AUTH).status_code == 200
