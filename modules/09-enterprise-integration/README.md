# Module 09 — Enterprise Systems and Integration

> **In plain words:** Companies already use many systems, and your app has to work with them. You'll connect AdmitFlow to the website, email, WhatsApp, a customer-management system (CRM) and company logins, without creating duplicates or security holes.
>
> **What you'll build:** Website enquiries arriving instantly, approved messages actually being sent, a sync to the marketing team's CRM, and sign-in with Google.
>
> **You can skip for now:** Lesson 07 (big platforms like SAP and Salesforce) is awareness only. The MCP server needs a newer Python; it's fine to read it first.
>
> **Comes after:** [Module 08: Generative AI Engineering](../08-generative-ai-engineering/README.md) · **Leads to:** [Module 10: Production Engineering, Security and Reliability](../10-production-security-reliability/README.md)
>
> **How to work through it:** read the lessons in order → try the exercises → do the build → do the break & fix → do the Field Track → tick the "Done when" list. New here? Read [Start Here](../../START-HERE.md) first.

**Stage:** 4 — Field-ready · **Time:** ~3 weeks at 15–20 h/week · **Builds:** C4 (Deploy and integrate)
**Prerequisites:** [Module 08](../08-generative-ai-engineering/README.md). Optional: a free developer account on a CRM.

## Outcome

After this module you can connect a new system to the messy reality of existing enterprise software, identity and permissions: signed webhooks, idempotent syncs, an outbox for messages, single sign-on, least-privilege service accounts, and an MCP server that lets AI assistants work with the system safely.

## Why this matters to an FDE

AdmitFlow is useful on its own; it becomes *part of how the institute works* when it's connected. Website enquiries arrive instantly; marketing's CRM stays in step; approved follow-ups actually reach students; staff sign in with their Google accounts; counsellors' AI assistants can look things up. Each connection is also a new way to fail or to leak data, and that's what security reviews will probe.

## Checkpoint

Already built webhooks, OAuth/OIDC sign-in and idempotent syncs? Take the [checkpoint](checkpoint.md). Score ≥ 80% **and** complete the [build](build.md) and [break & fix](break-and-fix/README.md) to move on.

## Lessons

| # | Lesson | Core / Stretch | Time |
| --- | --- | --- | --- |
| 01 | [The enterprise landscape](lessons/01-enterprise-landscape.md) | Core | 2 h |
| 02 | [Integration patterns](lessons/02-integration-patterns.md) | Core | 3 h |
| 03 | [Webhooks done right](lessons/03-webhooks.md) | Core | 3 h |
| 04 | [Calling third-party APIs reliably](lessons/04-calling-third-party-apis.md) | Core | 4 h |
| 05 | [Identity: OAuth, OpenID Connect, SAML and SSO](lessons/05-identity-and-sso.md) | Core | 4 h |
| 06 | [Permissions, multi-tenancy and audit](lessons/06-permissions-and-audit.md) | Core | 3 h |
| 07 | [Enterprise platforms](lessons/07-enterprise-platforms.md) | Core / Stretch | 3 h |
| 08 | [Model Context Protocol](lessons/08-mcp.md) | Core | 3 h |

## Practice

[exercises/](exercises/README.md): send signed webhooks, a CRM-owned consent field, an extra MCP tool, and a security review.

## Build: AdmitFlow, connected

See [build.md](build.md).

- **Reference solution:** [`integrations/`](../../projects/admitflow/admitflow/integrations/webhooks.py) (webhooks, messaging outbox, CRM sync, Google sign-in), [`mcp_server.py`](../../projects/admitflow/admitflow/mcp_server.py), [`tests/test_integrations.py`](../../projects/admitflow/tests/test_integrations.py), [`tests/test_mcp.py`](../../projects/admitflow/tests/test_mcp.py), [ADR-006](../../projects/admitflow/docs/adr/006-integrations.md)

## Break & fix

[break-and-fix/](break-and-fix/README.md): a "robust" CRM sync turned 99 students into 240 contacts. Make it idempotent.

## Field Track

See [field-track.md](field-track.md). Complete the client's security questionnaire.

## Done when

- [ ] A signed website submission creates a lead; a redelivery doesn't duplicate it; tampered, replayed or unsigned requests are rejected
- [ ] Only approved drafts are sent; failures stay approved and are retried
- [ ] CRM sync is idempotent even when responses are lost (tested)
- [ ] Google sign-in checks signature, audience, expiry, verified email and domain; unprovisioned users get 403
- [ ] The MCP server acts as one counsellor and has no tools with side effects beyond drafting
- [ ] Security review written
- [ ] [`progress/self-assessment.md`](../../progress/self-assessment.md) updated

## Resources

See [resources.md](resources.md).

---
*Last verified: 2026-11-21 · httpx 0.28, PyJWT 2.15 + cryptography, MCP Python SDK 2.3 (Python 3.10+). CRM and WhatsApp clients are tested against fakes; check each vendor's current API reference before connecting to a real account.*
