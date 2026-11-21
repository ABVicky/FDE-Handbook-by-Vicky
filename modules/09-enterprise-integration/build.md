# Module 09 Build — AdmitFlow, connected

**Time:** ~25–30 hours · **Capabilities:** C4

## Scenario

AdmitFlow is trusted by the admissions team. Next:
1. **Website enquiries** should arrive instantly, not via a daily email.
2. **Approved follow-ups** should actually reach students by email or WhatsApp.
3. **Marketing** wants every lead in their CRM, updated nightly.
4. Mr. Okafor: *"Staff should sign in with their Google accounts. And I want to see a security review before any of this goes live."*
5. Counsellors use an AI assistant app and ask: *"Can it look things up in AdmitFlow?"*

## Requirements

1. **Webhook** `POST /public/webhooks/website-form`: HMAC signature over timestamp + raw body, 5-minute window, event-ID idempotency (atomic in SQL), payload validation and normalization, correct status codes, fails closed when not configured
2. **Outbox** `admitflow send-approved`: sends only approved drafts via email (SMTP) or WhatsApp (provider HTTP API); records provider IDs and sent time; failures stay approved with a reason; `--dry-run`
3. **CRM sync** `admitflow crm-sync`: search-before-create, store `crm_id`, update thereafter; retries with backoff for safe operations; **no blind retry of creates**; report created/linked/updated/skipped/failed
4. **Google sign-in** `POST /auth/google`: verify signature (JWKS), issuer, audience, expiry, verified email and hosted domain; provisioned users only
5. **MCP server** `admitflow mcp --user <counsellor>`: `search_leads`, `get_lead`, `course_info`, `draft_followup`; scoped to the user; no send/update tools
6. **Storage:** `crm_id`, draft `sent_at`/`external_id`, processed events; migration `0003`; contract tests
7. **Tests:** fakes for CRM (including lost responses), WhatsApp and Google; no real network in tests
8. **Documents:** ADR for the integrations; [security review](#security-review)

## Security review

Write it with the [template](../../templates/security-review.md) (Exercise 04 is a full rehearsal). It must list every third party and the data each receives.

## Configuration (reference solution)

| Variable | For |
| --- | --- |
| `ADMITFLOW_WEBHOOK_SECRET` | Website webhook signatures |
| `SMTP_HOST`, `SMTP_PORT`, `SMTP_USERNAME`, `SMTP_PASSWORD`, `SMTP_FROM` | Email |
| `WHATSAPP_API_URL`, `WHATSAPP_TOKEN`, `WHATSAPP_PHONE_NUMBER_ID` | WhatsApp |
| `CRM_BASE_URL`, `CRM_TOKEN` | CRM sync |
| `ADMITFLOW_GOOGLE_CLIENT_ID`, `ADMITFLOW_SSO_DOMAIN` | Google sign-in |
| `ADMITFLOW_MCP_USER` | MCP server identity |

Install: `pip install -e ".[api,db,integrations,dev]"` (MCP needs Python 3.10+). Schedule `send-approved` every minute and `crm-sync` nightly (Module 06, Lesson 06).

## Done when

- [ ] All requirements implemented with tests; nothing in the test suite calls a real external service
- [ ] Break & fix duplicates eliminated, with a regression test
- [ ] Security review written and reviewed by a peer playing Mr. Okafor
- [ ] Field Track questionnaire completed

## Stretch

- CRM webhook for consent changes (Exercise 02)
- SCIM endpoint for automatic provisioning and deactivation
- "Sign in with Google" button in the React dashboard (Google Identity Services)
- Remote MCP server over streamable HTTP with OAuth
