# ADR-006: Integrations: push for enquiries, outbox for messages, one-way CRM sync, Google SSO, scoped MCP

**Status:** Accepted · **Date:** Module 09

## Context
AdmitFlow must connect to the website (enquiries), email/WhatsApp (follow-ups), marketing's CRM, Google Workspace (staff identity) and counsellors' AI assistant apps. The institute has one part-time IT administrator; every connection adds operational and security risk.

## Decisions
1. **Website → AdmitFlow by signed webhook** (HMAC over timestamp + body, 5-minute window, event-ID idempotency). The daily form export remains available for reconciliation.
2. **Messages by outbox:** only `approved` drafts are sent, by a scheduled worker; provider message IDs recorded; delivery is at-least-once (documented).
3. **CRM sync is one-way** (AdmitFlow → CRM), keyed by email; `crm_id` stored; creates never retried blindly. Consent stays owned by the CRM (future: read-only consent sync).
4. **Staff sign in with Google** (OIDC ID token verified server-side; `hd` restricted; provisioned users only). Passwords remain for break-glass admin access only.
5. **MCP server acts as one named counsellor,** read-and-draft only.

## Consequences
- ✅ Each integration fails independently and visibly; core AdmitFlow keeps working.
- ✅ No integration can send a message or change a lead without a person's approval (except the webhook creating/merging enquiries).
- ⚠️ At-least-once messaging: a crash at the wrong moment could send a duplicate. Accepted and documented.
- ⚠️ CRM search lag can delay linking after a lost response by one run.
- ➡️ SCIM provisioning, consent sync and a remote (HTTP) MCP server are follow-ups.
