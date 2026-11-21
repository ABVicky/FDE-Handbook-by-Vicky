"""Syncing leads to the institute's CRM (added in Module 09).

The client is written against a HubSpot-style contacts API (search, create, update). Endpoint paths
and fields vary by CRM and change over time: check the vendor's current API reference.

Idempotency is the whole game here:
1. If we've synced this lead before, we have its `crm_id`: **update**, never create.
2. Otherwise **search by email first**: the contact may exist (created by marketing, or by an
   earlier run that crashed before saving the ID).
3. Only then create, and **save the CRM's ID immediately**.
Reads and updates are retried with backoff on timeouts, 429 and 5xx. **Creates are never retried
blindly:** a timed-out create may have succeeded, so we search again before deciding. (Many CRMs' search
indexes lag a few seconds behind writes; if the contact isn't visible yet, we stop and retry next run.)
"""
from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional

log = logging.getLogger("admitflow.crm")
RETRYABLE = {429, 500, 502, 503, 504}


class CrmError(Exception):
    pass


class CrmTimeout(CrmError):
    """The request timed out: it may or may not have been applied by the CRM."""


class CrmClient:
    def __init__(self, base_url: str, token: str, client=None, attempts: int = 3,
                 sleep: Callable[[float], None] = time.sleep):
        import httpx

        self.base = base_url.rstrip("/")
        self.headers = {"Authorization": f"Bearer {token}"}
        self.client = client or httpx.Client(timeout=15)
        self.attempts, self.sleep = attempts, sleep

    def _request(self, method: str, path: str, json: Optional[dict] = None, retry: bool = True) -> dict:
        import httpx

        attempts = self.attempts if retry else 1
        for attempt in range(1, attempts + 1):
            try:
                response = self.client.request(method, self.base + path, json=json, headers=self.headers)
            except httpx.TimeoutException:
                if not retry:
                    raise CrmTimeout(f"{method} {path}: timed out") from None
                problem = "timeout"
            else:
                if response.status_code not in RETRYABLE:
                    if response.status_code >= 400:
                        raise CrmError(f"{method} {path}: HTTP {response.status_code} {response.text[:200]}")
                    return response.json() if response.content else {}
                problem = f"HTTP {response.status_code}"
            if attempt == attempts:
                raise CrmError(f"{method} {path}: gave up after {attempt} attempts ({problem})")
            self.sleep(2 ** (attempt - 1))
        raise CrmError("unreachable")  # pragma: no cover

    def find_by_email(self, email: str) -> Optional[str]:
        body = {"filterGroups": [{"filters": [{"propertyName": "email", "operator": "EQ", "value": email}]}], "limit": 1}
        results = self._request("POST", "/crm/v3/objects/contacts/search", body).get("results", [])
        return results[0]["id"] if results else None

    def create(self, properties: dict) -> str:
        # Never retried automatically: a timed-out create may have succeeded (see sync_leads).
        return self._request("POST", "/crm/v3/objects/contacts", {"properties": properties}, retry=False)["id"]

    def update(self, contact_id: str, properties: dict) -> None:
        self._request("PATCH", f"/crm/v3/objects/contacts/{contact_id}", {"properties": properties})


def contact_properties(lead) -> Dict[str, str]:
    first, _, last = lead.name.partition(" ")
    return {
        "email": lead.email,
        "firstname": first,
        "lastname": last,
        "phone": lead.phone or "",
        "admitflow_lead_id": lead.lead_id,
        "admitflow_course": lead.course or "",
        "admitflow_status": lead.status,
        "admitflow_channels": ";".join(lead.sources),
    }


@dataclass
class SyncReport:
    created: List[str] = field(default_factory=list)
    linked: List[str] = field(default_factory=list)    # existed in the CRM already; ID saved
    updated: List[str] = field(default_factory=list)
    skipped: List[tuple] = field(default_factory=list)
    failed: List[tuple] = field(default_factory=list)


def sync_leads(repo, crm: CrmClient, limit: int = 10_000) -> SyncReport:
    report = SyncReport()
    leads, _ = repo.list_leads(limit=limit)
    for lead in leads:
        if not lead.email:
            report.skipped.append((lead.lead_id, "no email (the CRM identifies contacts by email)"))
            continue
        try:
            properties = contact_properties(lead)
            if lead.crm_id:
                crm.update(lead.crm_id, properties)
                report.updated.append(lead.lead_id)
                continue
            existing = crm.find_by_email(lead.email)
            if existing:
                lead.crm_id = existing
                crm.update(existing, properties)
                report.linked.append(lead.lead_id)
            else:
                try:
                    lead.crm_id = crm.create(properties)
                    report.created.append(lead.lead_id)
                except CrmTimeout:
                    # The create may have gone through. Look before trying again, or we'd make a duplicate.
                    found = crm.find_by_email(lead.email)
                    if not found:
                        raise CrmError("create timed out and the contact isn't visible yet; will retry next run")
                    lead.crm_id = found
                    report.linked.append(lead.lead_id)
            repo.update_lead(lead)                      # save the link immediately
        except CrmError as exc:
            report.failed.append((lead.lead_id, str(exc)))
            log.warning("CRM sync failed for %s: %s", lead.lead_id, exc)
    return report
