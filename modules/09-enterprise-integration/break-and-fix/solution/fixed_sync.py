"""The same two nightly runs against the same flaky CRM, using AdmitFlow's idempotent sync."""
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3] / "projects" / "admitflow"
sys.path[:0] = [str(ROOT), str(HERE.parent)]
from admitflow.importers import import_file  # noqa: E402
from admitflow.integrations.crm import CrmClient, sync_leads  # noqa: E402
from admitflow.repository import JsonRepository  # noqa: E402
from flaky_crm import FlakyCrm  # noqa: E402

crm = FlakyCrm()
repo = JsonRepository(Path(tempfile.mkdtemp()) / "store.json")
repo.add_leads(import_file(ROOT / "data" / "leads_sample.csv", "website").leads)
client = CrmClient("https://crm.test", "token", client=crm.client(), sleep=lambda s: None)
first, second = sync_leads(repo, client), sync_leads(repo, client)
with_email = sum(1 for lead in repo.list_leads(limit=500)[0] if lead.email)
print(f"run 1: created {len(first.created)}, linked after a lost response {len(first.linked)}, failed {len(first.failed)}")
print(f"run 2: updated {len(second.updated)}, created {len(second.created)}")
print(f"leads with email: {with_email} · contacts in CRM: {len(crm.contacts)} · duplicates: {crm.duplicates()}")
assert crm.duplicates() == 0 and len(crm.contacts) == with_email
