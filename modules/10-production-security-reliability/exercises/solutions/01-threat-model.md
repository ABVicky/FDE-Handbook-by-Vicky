# Exercise 01 — Model answer (top risks)

| # | Component | Threat (STRIDE) | L | I | Control | Test |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Login | Spoofing: password guessing | M | H | Rate limit by username; Google SSO; generic errors | `test_login_is_rate_limited_and_audited` |
| 2 | Public assistant | DoS / cost abuse | H | M | IP rate limit; 500-char cap; provider spend limit | `test_public_endpoint_is_rate_limited` |
| 3 | Public assistant | Info disclosure via prompt injection | M | M | Only public course documents are retrievable; grounding | Injection cases in the evaluation set |
| 4 | Webhook | Spoofing / tampering / replay | M | M | HMAC over timestamp + body; 5-min window; idempotency | `test_signature_rejections`, `test_webhook_rejects_bad_requests` |
| 5 | Outbox | Elevation: sending unapproved text | L | H | Only `approved` drafts; approval is a separate authorized action, audited | `test_only_approved_drafts_are_sent` |
| 6 | MCP server | Info disclosure / elevation via an AI agent | M | H | Acts as one counsellor; same "not found"; no write/send tools; no contact details | `test_get_lead_hides_other_counsellors_leads`, `test_tools_are_read_and_draft_only` |
| 7 | Logs | Info disclosure | M | M | Redaction filter; IDs not names | `test_log_records_are_redacted` |
| 8 | Third-party tokens | Spoofing if leaked; outage if expired | M | H | Secret manager; inventory with expiry reminders; alerts | Module 10 break & fix |

**Gaps worth writing tests for next:** a counsellor can still read *any* lead's details via `GET /leads/{id}` (only changes are restricted). Is that the client's intended policy? Ask. If not, restrict reads too and test it.
