"""Replays three days of AdmitFlow's outbox, run hourly by a scheduler, as it happened.

Counsellors approve follow-ups through the day. On day 1 at 14:00 the WhatsApp provider token expires.
The scheduler runs `send-approved` every hour and ignores its exit code. Nobody is alerted.

Usage: python simulate_incident.py      (standard library + admitflow; no network)
"""
import logging
import sys
import tempfile
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3] / "projects" / "admitflow"
sys.path.insert(0, str(ROOT))
from admitflow.importers import import_file  # noqa: E402
from admitflow.integrations.messaging import SendError, send_approved  # noqa: E402
from admitflow.models import Draft  # noqa: E402
from admitflow.observability import metrics  # noqa: E402
from admitflow.repository import JsonRepository  # noqa: E402

START = datetime(2026, 9, 14, 8, 0)
TOKEN_EXPIRES = START + timedelta(hours=6)          # day 1, 14:00


class Clock:
    now = START


class ExpiringWhatsApp:
    def send(self, to, subject, body):
        if Clock.now >= TOKEN_EXPIRES:
            raise SendError("HTTP 401: access token has expired")
        return f"wamid.{abs(hash((to, body))) % 10**8}"


class Email:
    def send(self, to, subject, body):
        return f"email-{abs(hash(to)) % 10**6}"


def run(alert_check=None):
    workdir = Path(tempfile.mkdtemp())
    # The warnings went to a log file nobody read, exactly as in the real incident.
    handler = logging.FileHandler(workdir / "outbox.log")
    outbox_log = logging.getLogger("admitflow.outbox")
    outbox_log.handlers[:] = [handler]
    outbox_log.propagate = False
    repo = JsonRepository(workdir / "store.json")
    leads = [l for l in import_file(ROOT / "data" / "leads_sample.csv", "website").leads if l.email and l.phone]
    repo.add_leads(leads)
    senders = {"whatsapp": ExpiringWhatsApp(), "email": Email()}
    alerts = []
    n = 0
    for hour in range(72):
        Clock.now = START + timedelta(hours=hour)
        if 9 <= Clock.now.hour < 18:                # counsellors approve 2 drafts an hour in office hours
            for _ in range(2):
                lead = leads[n % len(leads)]
                channel = "whatsapp" if n % 3 else "email"
                repo.save_draft(Draft(f"d{n:03d}", lead.lead_id, channel, "Follow-up", "Hi!", "priya",
                                      Clock.now, status="approved", decided_by="priya", decided_at=Clock.now))
                n += 1
        report = send_approved(repo, senders)      # the hourly job; exit code ignored by the scheduler
        waiting = [d.decided_at for d in repo.list_drafts(status="approved")]
        oldest = (Clock.now - min(waiting)).total_seconds() / 60 if waiting else 0.0
        metrics.set("admitflow_outbox_oldest_approved_minutes", oldest)   # as seen at the simulated time
        if alert_check and alert_check(Clock.now):
            alerts.append(Clock.now)
    stuck = repo.list_drafts(status="approved")
    sent = repo.list_drafts(status="sent")
    handler.close()
    warnings = (workdir / "outbox.log").read_text().count("send failed")
    return {"approved": n, "sent": len(sent), "stuck": len(stuck), "log_warnings": warnings,
            "log_file": workdir / "outbox.log",
            "oldest_stuck": min(d.decided_at for d in stuck) if stuck else None, "alerts": alerts}


if __name__ == "__main__":
    result = run()
    print(f"follow-ups approved over 3 days: {result['approved']}")
    print(f"sent: {result['sent']}   still waiting: {result['stuck']}   (oldest approved {result['oldest_stuck']:%a %H:%M})")
    print(f"warnings written to the log: {result['log_warnings']}   alerts raised: {len(result['alerts'])}")
    print(f"(log file: {result['log_file']})")
    print("\nFirst anyone heard of it: Thursday 10:15, a parent called: 'Nobody replied to my son on WhatsApp.'")
