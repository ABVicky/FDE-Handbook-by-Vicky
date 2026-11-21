"""The contractor's CRM sync. "Robust: retries on any network error!"

Usage: python naive_crm_sync.py   (needs httpx)
"""
import sys
import time
from pathlib import Path

import httpx

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "projects" / "admitflow"))
from admitflow.importers import import_file  # noqa: E402
from flaky_crm import FlakyCrm  # noqa: E402

DATA = Path(__file__).resolve().parents[3] / "projects" / "admitflow" / "data"


def create_contact(client, lead, attempts=3):
    for attempt in range(attempts):
        try:
            response = client.post("/crm/v3/objects/contacts",
                                   json={"properties": {"email": lead.email, "firstname": lead.name}})
            return response.json()["id"]
        except httpx.TransportError:
            time.sleep(0.01)                # retry!
    raise RuntimeError("CRM unreachable")


def sync(client, leads):
    for lead in leads:
        if lead.email:
            create_contact(client, lead)


if __name__ == "__main__":
    crm = FlakyCrm()
    leads = import_file(DATA / "leads_sample.csv", "website").leads
    sync(crm.client(), leads)
    sync(crm.client(), leads)               # it runs every night
    with_email = sum(1 for lead in leads if lead.email)
    print(f"leads with email: {with_email}")
    print(f"contacts in CRM:  {len(crm.contacts)}")
    print(f"duplicates:       {crm.duplicates()}")
