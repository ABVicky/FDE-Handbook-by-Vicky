# Lesson 02 — Protecting data: encryption, secrets, minimization and retention

**Time:** ~3 hours · **Core**

## Encryption

| Where | How | AdmitFlow |
| --- | --- | --- |
| **In transit** | TLS (HTTPS) everywhere: browser ↔ API, API ↔ database, API ↔ third parties | Managed HTTPS on the platform; `Strict-Transport-Security` header; database connections over TLS |
| **At rest** | Disk/database encryption (usually on by default in managed cloud services) | Managed PostgreSQL encrypted at rest; backups encrypted |
| **Application-level** | Encrypting specific fields yourself | Not needed yet; consider for highly sensitive fields (e.g. ID documents) |

Passwords are **hashed**, not encrypted (Module 04): there's no way back to the original.

## Secrets

Recap from Module 06, Lesson 07, plus an inventory. Every credential should have an owner, a scope, a storage place, an expiry and a rotation plan:

| Secret | Scope | Stored | Expires / rotation |
| --- | --- | --- | --- |
| `ADMITFLOW_SECRET_KEY` | Signs sessions | Secret manager | Rotate yearly (logs everyone out) |
| Database password | AdmitFlow DB user (no DDL in production) | Secret manager | Yearly |
| `ADMITFLOW_WEBHOOK_SECRET` | Website → AdmitFlow | Both secret managers | Yearly, with overlap |
| WhatsApp / SMTP / CRM tokens | Send / sync only | Secret manager | **Check provider expiry** (the Module 10 incident) |
| LLM API key | Model calls; spending limit set | Secret manager | Yearly; budget alerts |
| `ADMITFLOW_METRICS_TOKEN` | Read metrics | Monitoring system | Yearly |

## Data minimization

Collect, keep and share only what you need.
- **Don't import** columns you don't use (Module 05).
- **Don't send** more than necessary to third parties. AdmitFlow's drafter now sends the student's **first name only** and **masks phone numbers and emails** in notes before they reach the language model ([`llm.py`](../../../projects/admitflow/admitflow/llm.py), tested in `test_drafter_sends_minimal_personal_data`).
- **Don't log** personal data. A `RedactingFilter` masks emails and phone numbers in every log line ([`privacy.py`](../../../projects/admitflow/admitflow/privacy.py)):

```python
redact("Call +1 202-555-0141 or grace.patel@example.com")
# 'Call [phone] or g***@example.com'
redact("fee 1,800, ENQ-0001, 2026-09-01 10:55")
# unchanged: dates, fees and IDs aren't phone numbers
```

Writing that filter showed a classic trap: the first version also masked timestamps, which would have made the logs useless for investigating incidents. Test redaction on realistic log lines, not just on phone numbers.

Masking is a safety net, not a licence: log IDs (`lead_id`), not names and contact details, in the first place.

## Retention and deletion

Keep personal data only as long as needed, and be able to delete it on request.
- Agree a **retention policy** with the client (e.g. delete or anonymize leads 24 months after last contact unless they enrolled; enrolled students move to the SIS).
- Implement it as a **scheduled job**, with an audit entry for every deletion.
- Handle **deletion requests:** remove from AdmitFlow, the CRM (via its API), drafts and notes; log the request (not the deleted data).
- Remember **backups**: deleted data persists in backups until they expire. Document this in the privacy notice.

## Data residency and processors

Every third party that processes students' data (hosting, CRM, messaging, AI provider) is a **processor** under most data-protection laws. The client needs a contract with each, and needs to know where data is stored and processed. Your job: list them accurately (the security review) and choose regions and settings that match the client's obligations.

## Check yourself

Implement `admitflow purge --older-than-months 24 --dry-run`: list (and with `--apply`, anonymize) leads with no activity for 24 months that aren't enrolled, writing one audit event per lead. Anonymize rather than delete if reports need the counts. What happens to their notes and drafts?

Next: [Lesson 03 — Protecting against abuse](03-abuse-protection.md)
