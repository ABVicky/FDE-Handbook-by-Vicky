"""Exercise 01 — reference: act as the website and send signed webhooks to AdmitFlow (in-process).

Run: python webhook_sender.py   (needs admitflow with the api extra)
"""
import json
import os
import sys
import tempfile
import time
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4] / "projects" / "admitflow"
sys.path.insert(0, str(ROOT))
SECRET = "whsec_exercise_secret_0123456789"
os.environ["ADMITFLOW_WEBHOOK_SECRET"] = SECRET
os.environ.setdefault("ADMITFLOW_SECRET_KEY", "exercise-secret-key-long-enough-0123456789")

from fastapi.testclient import TestClient  # noqa: E402

from admitflow.api import create_app  # noqa: E402
from admitflow.integrations.webhooks import sign  # noqa: E402
from admitflow.repository import JsonRepository  # noqa: E402

repo = JsonRepository(Path(tempfile.mkdtemp()) / "store.json")
client = TestClient(create_app(repo))


def send(payload, event_id=None, timestamp=None, tamper=False):
    event_id = event_id or f"evt_{uuid.uuid4().hex[:16]}"
    body = json.dumps(payload).encode()
    ts = str(timestamp or int(time.time()))
    signature = sign(SECRET, ts, body)
    if tamper:
        body = body.replace(b"Accounting", b"Nursing")          # changed after signing
    headers = {"X-AdmitFlow-Event-Id": event_id, "X-AdmitFlow-Timestamp": ts,
               "X-AdmitFlow-Signature": signature, "Content-Type": "application/json"}
    response = client.post("/public/webhooks/website-form", content=body, headers=headers)
    return response.status_code, response.json()


forms = [
    {"name": "Lucía Fernández", "email": "lucia@example.net", "course": "Accounting"},
    {"name": "Kofi Asante", "phone": "202 555 0188", "course": "web_dev"},
    {"name": "MEI WANG", "email": "Mei.Wang@Example.org", "course": "DA"},
    {"name": "Arash Karimi", "email": "arash@example.net", "message": "Evening batch?"},
    {"name": "Nia Ndlovu", "phone": "(202) 555-0166"},
]
results = [send(form, event_id=f"evt_exercise_{i:04d}") for i, form in enumerate(forms)]
assert all(r == (200, {"status": "created"}) for r in results), results
assert send(forms[0], event_id="evt_exercise_0000") == (200, {"status": "duplicate"})
assert send({"name": "Tamper Test", "email": "t@example.net", "course": "Accounting"}, tamper=True)[0] == 401
assert send({"name": "Old Request", "email": "o@example.net"}, timestamp=int(time.time()) - 600)[0] == 401
assert send({"name": "No Contact"})[0] == 422

leads, total = repo.list_leads()
assert total == 5
print("\n".join(f"{l.lead_id:<26} {l.name:<18} {l.email or l.phone:<26} {l.course}" for l in leads))
print("\nall checks passed")
