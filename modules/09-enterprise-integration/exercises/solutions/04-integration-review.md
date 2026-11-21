# Exercise 04 — What a strong review covers (excerpt)

**Third parties and data shared**

| Service | Data sent | Region / terms to confirm |
| --- | --- | --- |
| Hosting (cloud provider) | Everything | Region allowed by the institute; backups in the same jurisdiction |
| LLM provider (if `ADMITFLOW_LLM=claude`) | Course documents; for drafts: first name, course, recent notes | Retention and training-use terms; minimize note content; can be switched off |
| CRM | Name, email, phone, course, status | Existing marketing contract; consent ownership |
| Email (SMTP via Google Workspace) | Recipient, message | Covered by the institute's Workspace agreement |
| WhatsApp Business provider | Phone, message | Opt-in requirements; template approval |
| Google sign-in | Staff identity only | Workspace domain restriction (`hd`) |

**Identity and access:** staff sign in with Google (2-step verification enforced by IT); AdmitFlow sessions last 8 hours; roles counsellor/admin; counsellors act only on assigned or unassigned leads; leavers lose access when IT disables their Google account (within one session); SCIM provisioning is a known gap.

**Service credentials:** webhook secret, CRM private-app token, SMTP app password, WhatsApp token, LLM API key, database password: each in the secret manager, one per integration, least scope, owner named, rotation every 6 months.

**AI controls:** answers only from current course documents with verified citations, and "I don't know" otherwise; drafts are pending until a person approves; the MCP server acts as one counsellor and has no send/update tools; prompt-injection cases in the evaluation set run in CI.

**Known gaps (examples):** no SCIM yet (manual leaver process: weekly review); public assistant not yet rate-limited (Module 10); audit log not yet append-only (Module 10); WhatsApp templates not approved yet; no penetration test yet.
