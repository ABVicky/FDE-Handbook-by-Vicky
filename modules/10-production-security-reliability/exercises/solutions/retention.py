"""Exercise 02 — reference: anonymize inactive leads under a retention policy. Run: python retention.py"""
import sys
import tempfile
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4] / "projects" / "admitflow"
sys.path.insert(0, str(ROOT))
from admitflow.importers import import_file  # noqa: E402
from admitflow.models import AuditEvent, Note  # noqa: E402
from admitflow.repository import JsonRepository  # noqa: E402

ANON_NAME = "Former enquirer"


def purge_inactive(repo, now, months=24, apply=False):
    cutoff = now - timedelta(days=round(months * 30.44))
    leads, _ = repo.list_leads(limit=1_000_000)
    candidates = []
    for lead in leads:
        if lead.status == "enrolled" or lead.name == ANON_NAME:
            continue                                         # never touch enrolled; idempotent
        notes = repo.notes_for(lead.lead_id)
        last_activity = max([lead.received_at] + [n.created_at for n in notes])
        if last_activity < cutoff:
            candidates.append(lead)
    if apply:
        for lead in candidates:
            lead.name, lead.email, lead.phone, lead.notes = ANON_NAME, None, None, ""
            repo.update_lead(lead)
            repo.add_audit(AuditEvent(now, "retention-job", "retention.anonymize", lead.lead_id,
                                      f"inactive since before {cutoff:%Y-%m-%d}"))
            # Notes may contain personal data too. The repository has no "delete notes" operation yet;
            # in a real system you'd add one (and remove drafts), and document that backups expire after N days.
    return [lead.lead_id for lead in candidates]


if __name__ == "__main__":
    repo = JsonRepository(Path(tempfile.mkdtemp()) / "s.json")
    repo.add_leads(import_file(ROOT / "data" / "leads_sample.csv", "website").leads)   # all from Sept 2026
    enrolled = repo.get_lead("ENQ-0001")
    enrolled.status = "enrolled"
    repo.update_lead(enrolled)
    repo.add_note(Note("ENQ-0002", "priya", "Still interested, call in 2029", datetime(2028, 10, 1)))

    now = datetime(2028, 11, 1)                              # 26 months later
    dry = purge_inactive(repo, now)
    assert "ENQ-0001" not in dry and "ENQ-0002" not in dry and len(dry) == 118
    assert repo.get_lead("ENQ-0003").email is not None       # dry run changes nothing
    done = purge_inactive(repo, now, apply=True)
    assert done == dry and repo.get_lead("ENQ-0003").name == ANON_NAME and repo.get_lead("ENQ-0003").email is None
    assert repo.get_lead("ENQ-0003").course is not None      # kept for reports
    assert len(repo.list_audit(action="retention.", limit=1000)) == 118    # list_audit returns 100 by default
    assert purge_inactive(repo, now, apply=True) == []       # safe to run twice
    print("all checks passed")
