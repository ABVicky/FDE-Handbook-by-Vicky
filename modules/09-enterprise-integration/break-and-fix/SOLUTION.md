# Break & Fix — Solution

> ⚠️ Try it properly first.

## Two mechanisms, both "retries"

| # | Mechanism | Why it duplicates |
| --- | --- | --- |
| 1 | **Retrying a non-idempotent request.** `create_contact` retries the `POST` after a timeout | A timeout doesn't mean failure. The CRM often *did* create the contact; the retry creates another |
| 2 | **No memory between runs.** The script never stores the CRM's contact ID, and never checks whether a contact exists | Every nightly run creates everyone again |

## The fix

AdmitFlow's sync ([`integrations/crm.py`](../../../projects/admitflow/admitflow/integrations/crm.py)):

1. If the lead has a `crm_id`, **update**; never create.
2. Otherwise **search by email**; if found, link it (save the ID) and update.
3. Only then **create**, and save the ID **immediately** (`repo.update_lead`).
4. **Creates are never retried blindly.** On a timeout, search again: if the contact appeared, link it; if not, stop and let the next run retry. Reads and updates *are* retried with backoff (they're idempotent).

```bash
python solution/fixed_sync.py
```

```
run 1: created 80, linked after a lost response 19, failed 0
run 2: updated 99, created 0
leads with email: 99 · contacts in CRM: 99 · duplicates: 0
```

The same scenario is a permanent regression test: `test_crm_timeout_after_create_does_not_duplicate` in [`tests/test_integrations.py`](../../../projects/admitflow/tests/test_integrations.py).

**Real-world caveat:** many CRMs' search indexes update a few seconds after a write. A search right after a timed-out create can miss the new contact. AdmitFlow then *stops* rather than creating again, and the next run links it. Some APIs support **idempotency keys** (send a unique key with the create; the server ignores repeats), which is the cleanest fix when available. Check the vendor's documentation.

## Cleaning up the existing duplicates (plan)

1. **Stop the bleeding:** disable the old script before anything else.
2. **Export** all contacts, and back up the CRM (or use its recycle bin/merge features).
3. **Group by normalized email**; within each group keep the oldest contact (it may carry marketing history), and use the CRM's **merge** feature rather than delete, so activity history and unsubscribes are preserved. Never lose an unsubscribe.
4. Do a **dry run** on 10 groups with marketing watching; then the rest in batches.
5. Run AdmitFlow's sync once to link every lead to its surviving contact (`crm_id`).
6. Tell marketing what happened and how many students may have received duplicates.

## The general lesson

Every integration runs on an unreliable network. Ask of every write: *"What happens if this runs twice?"* Make writes idempotent (check, link, store the ID, use idempotency keys), and treat "timeout" as "unknown," never as "failed."
