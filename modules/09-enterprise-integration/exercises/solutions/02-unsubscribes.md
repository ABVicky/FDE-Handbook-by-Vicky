# Exercise 02 — Model answer

## Field ownership

| Field | System of record | AdmitFlow behaviour |
| --- | --- | --- |
| `unsubscribed` (marketing consent) | **CRM** | Read on every sync; never written by AdmitFlow |
| `status`, `course`, `assigned_to` | AdmitFlow | Written to the CRM |
| Contact details | AdmitFlow (from enquiries) | Written to the CRM; CRM edits are not pulled back (one-way) |

## Design

- Add `unsubscribed: bool = False` and `unsubscribed_at` to `Lead`; Alembic migration (nullable/default false, so it's backward compatible).
- In `sync_leads`, after search/update, **read** the CRM's consent property (e.g. `hs_email_optout` on HubSpot-style CRMs; confirm the real property name with the client's CRM admin) and set the flag on the lead. Never include it in the properties AdmitFlow writes.
- In `send_approved`, before sending: if `lead.unsubscribed`, **skip** with reason `"unsubscribed in CRM"` and set the draft to `rejected` (so it isn't retried forever), recording `decided_by="system"`.
- Dedupe (`_merge`) must keep `unsubscribed=True` if *either* record has it: a new enquiry never silently re-subscribes someone. (They might want to hear back about *this* enquiry, so a counsellor can call them; that's a human decision, not an automatic resubscribe.)
- Sync frequency: nightly is too slow for consent. Run the consent read every 15 minutes, or use the CRM's webhook for subscription changes.

## Tests (sketch)

```python
def test_unsubscribe_is_read_not_written(repo, crm):
    fake, client = crm
    sync_leads(repo, client)
    contact_id = repo.get_lead("ENQ-0001").crm_id
    fake.contacts[contact_id]["unsubscribed"] = "true"
    sync_leads(repo, client)
    assert repo.get_lead("ENQ-0001").unsubscribed is True
    assert "unsubscribed" not in fake.last_written_properties        # AdmitFlow never writes it

def test_outbox_skips_unsubscribed(repo):
    ...  # approved draft for an unsubscribed lead → skipped with reason, status rejected, nothing sent

def test_new_enquiry_keeps_unsubscribe(repo):
    ...  # merge an unsubscribed lead with a fresh website enquiry → still unsubscribed
```

## Dashboard

Show a clear badge ("Unsubscribed from messages: call only if they contacted us") and disable the "Draft follow-up" button for those leads.
