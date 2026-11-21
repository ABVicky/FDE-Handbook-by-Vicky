import pytest
from fastapi.testclient import TestClient

from course_service import create_app

TOKEN = "test-admin-token"
ADMIN = {"Authorization": f"Bearer {TOKEN}"}
DA = {"code": "DA101", "name": "Data Analytics", "campus": "North", "fee": 1200, "seats": 30}


@pytest.fixture
def client():
    return TestClient(create_app(admin_token=TOKEN))


def test_create_and_get(client):
    assert client.post("/courses", json=DA, headers=ADMIN).status_code == 201
    assert client.get("/courses/DA101").json()["name"] == "Data Analytics"


@pytest.mark.parametrize("headers", [{}, {"Authorization": "Bearer wrong"}, {"Authorization": TOKEN}])
def test_create_requires_admin_token(client, headers):
    assert client.post("/courses", json=DA, headers=headers).status_code == 401


def test_duplicate_code_is_409(client):
    client.post("/courses", json=DA, headers=ADMIN)
    assert client.post("/courses", json=DA, headers=ADMIN).status_code == 409


@pytest.mark.parametrize(
    "field, value",
    [("code", "da101"), ("code", "X"), ("campus", "East"), ("fee", 0), ("seats", 0), ("seats", 500), ("name", "")],
)
def test_validation(client, field, value):
    response = client.post("/courses", json={**DA, field: value}, headers=ADMIN)
    assert response.status_code == 422
    assert field in str(response.json())


def test_missing_course_is_404(client):
    assert client.get("/courses/NOPE").status_code == 404
    assert client.patch("/courses/NOPE", json={"fee": 10}, headers=ADMIN).status_code == 404


def test_patch_updates_only_given_fields(client):
    client.post("/courses", json=DA, headers=ADMIN)
    body = client.patch("/courses/DA101", json={"fee": 1350}, headers=ADMIN).json()
    assert body["fee"] == 1350 and body["seats"] == 30
    assert client.patch("/courses/DA101", json={"seats": 999}, headers=ADMIN).status_code == 422
    assert client.patch("/courses/DA101", json={"fee": 1}).status_code == 401


def test_list_filter_and_pagination(client):
    for n in range(7):
        client.post("/courses", json={**DA, "code": f"C{n}", "campus": "North" if n % 2 else "South"}, headers=ADMIN)
    north = client.get("/courses", params={"campus": "North"}).json()
    assert north["total"] == 3
    page2 = client.get("/courses", params={"page": 2, "page_size": 5}).json()
    assert [c["code"] for c in page2["items"]] == ["C5", "C6"] and page2["total"] == 7
    assert client.get("/courses", params={"page_size": 51}).status_code == 422


def test_create_app_requires_token(monkeypatch):
    monkeypatch.delenv("ADMIN_TOKEN", raising=False)
    with pytest.raises(RuntimeError):
        create_app()
