"""Integrations (Module 09): signed webhooks, the outbox, CRM sync, Google sign-in."""
import json
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import SimpleNamespace

import pytest

from admitflow.importers import import_file
from admitflow.integrations.messaging import RecordingSender, send_approved
from admitflow.integrations.webhooks import WebhookError, sign, verify
from admitflow.models import Draft, User
from admitflow.repository import JsonRepository

DATA = Path(__file__).resolve().parent.parent / "data"
SECRET = "whsec_test_secret_value_1234567890"


@pytest.fixture
def repo(tmp_path):
    repo = JsonRepository(tmp_path / "store.json")
    repo.add_leads(import_file(DATA / "leads_sample.csv", "website").leads)
    return repo


# -- webhook signatures -----------------------------------------------------------------------

def test_signature_round_trip():
    body, ts = b'{"name":"Zoe"}', "1790000000"
    verify(SECRET, ts, body, sign(SECRET, ts, body), now=1790000010)


@pytest.mark.parametrize(
    "timestamp, body, signature, now, problem",
    [
        ("1790000000", b"{}", None, 1790000000, "missing"),
        ("abc", b"{}", "sha256=x", 1790000000, "bad timestamp"),
        ("1790000000", b"{}", sign(SECRET, "1790000000", b"{}"), 1790000000 + 301, "replay"),
        ("1790000000", b'{"name":"evil"}', sign(SECRET, "1790000000", b"{}"), 1790000000, "mismatch"),
        ("1790000000", b"{}", sign("other-secret", "1790000000", b"{}"), 1790000000, "mismatch"),
    ],
)
def test_signature_rejections(timestamp, body, signature, now, problem):
    with pytest.raises(WebhookError, match=problem):
        verify(SECRET, timestamp, body, signature, now=now)


# -- webhook endpoint ---------------------------------------------------------------------------

@pytest.fixture
def api(repo, monkeypatch):
    pytest.importorskip("fastapi")
    from fastapi.testclient import TestClient

    from admitflow.api import create_app

    monkeypatch.setenv("ADMITFLOW_SECRET_KEY", "test-secret-key-that-is-long-enough-1234567890")
    monkeypatch.setenv("ADMITFLOW_WEBHOOK_SECRET", SECRET)
    return TestClient(create_app(repo))


def post_form(client, payload, event_id="evt_0001abcd", secret=SECRET, timestamp=None):
    body = json.dumps(payload).encode()
    ts = timestamp or str(int(time.time()))
    headers = {"X-AdmitFlow-Timestamp": ts, "X-AdmitFlow-Signature": sign(secret, ts, body),
               "X-AdmitFlow-Event-Id": event_id, "Content-Type": "application/json"}
    return client.post("/public/webhooks/website-form", content=body, headers=headers)


FORM = {"name": "  ZOË GARCÍA ", "email": "Zoe.Garcia@Example.org", "phone": "(202) 555-0199",
        "course": "web_dev", "message": "Is there an evening batch?"}


def test_webhook_creates_a_normalized_lead(api, repo):
    assert post_form(api, FORM).json() == {"status": "created"}
    lead = repo.get_lead("WEB-evt_0001abcd")
    assert (lead.name, lead.email, lead.phone, lead.course) == (
        "Zoë García", "zoe.garcia@example.org", "+12025550199", "Web Development")


def test_redelivered_event_is_idempotent(api, repo):
    post_form(api, FORM)
    assert post_form(api, FORM).json() == {"status": "duplicate"}
    assert repo.list_leads(search="zoe.garcia")[1] == 1


def test_existing_person_is_merged(api, repo):
    form = {"name": "Grace Patel", "email": "grace.patel91@example.com"}
    assert post_form(api, form, event_id="evt_grace0001").json() == {"status": "merged"}
    assert repo.list_leads()[1] == 120


@pytest.mark.parametrize(
    "kwargs, status",
    [({"secret": "wrong-secret"}, 401), ({"timestamp": "1000000000"}, 401), ({"event_id": "bad id!"}, 400)],
)
def test_webhook_rejects_bad_requests(api, kwargs, status):
    assert post_form(api, FORM, **kwargs).status_code == status


@pytest.mark.parametrize("payload", [{"email": "a@b.com"}, {"name": "No Contact"}, {"name": "123", "email": "a@b.com"}])
def test_webhook_rejects_invalid_forms(api, payload):
    assert post_form(api, payload, event_id="evt_invalid01").status_code == 422


def test_webhook_unconfigured_is_503(api, monkeypatch):
    monkeypatch.delenv("ADMITFLOW_WEBHOOK_SECRET")
    assert post_form(api, FORM).status_code == 503


# -- outbox -------------------------------------------------------------------------------------

def draft(draft_id, lead_id, status, channel="email"):
    return Draft(draft_id, lead_id, channel, "Hello", "Hi there", "priya", datetime(2026, 9, 20, 10), status=status)


def test_only_approved_drafts_are_sent(repo):
    repo.save_draft(draft("d1", "ENQ-0001", "approved"))
    repo.save_draft(draft("d2", "ENQ-0002", "pending_approval"))
    repo.save_draft(draft("d3", "ENQ-0003", "rejected"))
    sender = RecordingSender()
    report = send_approved(repo, {"email": sender})
    assert report.sent == ["d1"] and [m["to"] for m in sender.sent] == ["grace.patel91@example.com"]
    sent = repo.get_draft("d1")
    assert sent.status == "sent" and sent.external_id == "local-1" and sent.sent_at
    assert repo.get_draft("d2").status == "pending_approval"
    assert send_approved(repo, {"email": sender}).sent == []            # running again sends nothing new


def test_failed_send_stays_approved_and_is_retried(repo):
    repo.save_draft(draft("d1", "ENQ-0001", "approved"))
    failing = RecordingSender(fail_for={"grace.patel91@example.com"})
    report = send_approved(repo, {"email": failing})
    assert report.failed and repo.get_draft("d1").status == "approved"
    assert "send failed" in repo.get_draft("d1").reason
    assert send_approved(repo, {"email": RecordingSender()}).sent == ["d1"]


def test_missing_channel_or_address_is_skipped(repo):
    repo.save_draft(draft("d1", "ENQ-0001", "approved", channel="whatsapp"))
    report = send_approved(repo, {"email": RecordingSender()})
    assert report.skipped == [("d1", "no sender configured for whatsapp")]


def test_whatsapp_sender_uses_the_http_api():
    httpx = pytest.importorskip("httpx")
    from admitflow.integrations.messaging import SendError, WhatsAppCloudSender

    seen = []

    def handler(request):
        seen.append(request)
        if json.loads(request.content)["to"] == "12025550000":
            return httpx.Response(400, json={"error": {"message": "not a WhatsApp number"}})
        return httpx.Response(200, json={"messages": [{"id": "wamid.ABC"}]})

    sender = WhatsAppCloudSender("https://example.test/v1", "token", "12345",
                                 client=httpx.Client(transport=httpx.MockTransport(handler)))
    assert sender.send("+12025550141", "subject", "Hi Grace") == "wamid.ABC"
    assert seen[0].url.path == "/v1/12345/messages" and seen[0].headers["Authorization"] == "Bearer token"
    with pytest.raises(SendError, match="HTTP 400"):
        sender.send("+12025550000", "s", "b")


# -- CRM sync -------------------------------------------------------------------------------------

class FakeCrm:
    """An in-memory CRM behind httpx.MockTransport. Can time out after applying a create."""

    def __init__(self):
        self.contacts = {}
        self.timeout_after_create = 0   # how many creates should "succeed but time out"
        self.fail_next = 0              # how many requests return 503 first

    def handler(self, request):
        import httpx

        if self.fail_next:
            self.fail_next -= 1
            return httpx.Response(503)
        body = json.loads(request.content) if request.content else {}
        if request.url.path.endswith("/search"):
            email = body["filterGroups"][0]["filters"][0]["value"]
            hits = [{"id": cid} for cid, props in self.contacts.items() if props["email"] == email]
            return httpx.Response(200, json={"results": hits})
        if request.method == "POST":
            contact_id = str(1000 + len(self.contacts))
            self.contacts[contact_id] = body["properties"]
            if self.timeout_after_create:
                self.timeout_after_create -= 1
                raise httpx.ReadTimeout("response lost", request=request)
            return httpx.Response(201, json={"id": contact_id})
        if request.method == "PATCH":
            self.contacts[request.url.path.rsplit("/", 1)[1]].update(body["properties"])
            return httpx.Response(200, json={})
        return httpx.Response(404)


@pytest.fixture
def crm():
    httpx = pytest.importorskip("httpx")
    from admitflow.integrations.crm import CrmClient

    fake = FakeCrm()
    client = CrmClient("https://crm.test", "token", client=httpx.Client(transport=httpx.MockTransport(fake.handler)),
                       sleep=lambda s: None)
    return fake, client


def test_crm_sync_creates_then_updates(repo, crm):
    from admitflow.integrations.crm import sync_leads

    fake, client = crm
    first = sync_leads(repo, client)
    with_email = sum(1 for lead in repo.list_leads(limit=500)[0] if lead.email)
    assert len(first.created) == with_email == len(fake.contacts)
    assert len(first.skipped) == 120 - with_email
    second = sync_leads(repo, client)
    assert second.created == [] and len(second.updated) == with_email and len(fake.contacts) == with_email


def test_crm_links_contacts_that_already_exist(repo, crm):
    from admitflow.integrations.crm import sync_leads

    fake, client = crm
    fake.contacts["999"] = {"email": "grace.patel91@example.com"}       # created earlier by marketing
    report = sync_leads(repo, client)
    assert "ENQ-0001" in report.linked and repo.get_lead("ENQ-0001").crm_id == "999"


def test_crm_timeout_after_create_does_not_duplicate(repo, crm):
    """The break & fix scenario: the CRM saved the contact but the response was lost."""
    from admitflow.integrations.crm import sync_leads

    fake, client = crm
    fake.timeout_after_create = 3
    report = sync_leads(repo, client)
    emails = [c["email"] for c in fake.contacts.values()]
    assert len(emails) == len(set(emails))                               # no duplicates
    assert len(report.linked) == 3 and not report.failed


def test_crm_retries_transient_errors(repo, crm):
    from admitflow.integrations.crm import sync_leads

    fake, client = crm
    fake.fail_next = 2
    assert not sync_leads(repo, client).failed


# -- Google sign-in -------------------------------------------------------------------------------

@pytest.fixture(scope="module")
def rsa_key():
    pytest.importorskip("cryptography")
    from cryptography.hazmat.primitives.asymmetric import rsa

    return rsa.generate_private_key(public_exponent=65537, key_size=2048)


def google_token(key, **overrides):
    import jwt

    now = datetime.now(timezone.utc)
    claims = {"iss": "https://accounts.google.com", "aud": "client-123.apps.googleusercontent.com",
              "sub": "1234567890", "email": "Priya@northbridge.example", "email_verified": True,
              "hd": "northbridge.example", "name": "Priya Nair", "iat": now, "exp": now + timedelta(minutes=5)}
    claims.update(overrides)
    return jwt.encode(claims, key, algorithm="RS256", headers={"kid": "test-key"})


def fake_jwks(key):
    return SimpleNamespace(get_signing_key_from_jwt=lambda token: SimpleNamespace(key=key.public_key()))


def test_google_token_verification(rsa_key):
    from admitflow.integrations.oidc import SsoError, verify_google_id_token

    args = ("client-123.apps.googleusercontent.com", "northbridge.example")
    identity = verify_google_id_token(google_token(rsa_key), *args, jwks_client=fake_jwks(rsa_key))
    assert identity.email == "priya@northbridge.example"
    for bad in ({"aud": "someone-elses-app"}, {"hd": "gmail.com"}, {"email_verified": False},
                {"iss": "https://evil.example"}, {"exp": datetime.now(timezone.utc) - timedelta(minutes=1)}):
        with pytest.raises(SsoError):
            verify_google_id_token(google_token(rsa_key, **bad), *args, jwks_client=fake_jwks(rsa_key))


def test_google_login_endpoint(api, repo, rsa_key, monkeypatch):
    monkeypatch.setenv("ADMITFLOW_GOOGLE_CLIENT_ID", "client-123.apps.googleusercontent.com")
    monkeypatch.setenv("ADMITFLOW_SSO_DOMAIN", "northbridge.example")
    api.app.state.google_jwks = fake_jwks(rsa_key)
    token = google_token(rsa_key)
    assert api.post("/auth/google", json={"id_token": token}).status_code == 403     # not provisioned yet
    repo.save_user(User("priya@northbridge.example", "Priya Nair", "counsellor", "!sso-only"))
    body = api.post("/auth/google", json={"id_token": token}).json()
    assert body["username"] == "priya@northbridge.example" and body["access_token"]
    assert api.post("/auth/google", json={"id_token": google_token(rsa_key, hd="gmail.com")}).status_code == 401


def test_google_login_unconfigured(api, monkeypatch):
    monkeypatch.delenv("ADMITFLOW_GOOGLE_CLIENT_ID", raising=False)
    assert api.post("/auth/google", json={"id_token": "x" * 20}).status_code == 503
