# Module 09 — Checkpoint

Pass mark: **10 / 12**, plus the [build](build.md) and [break & fix](break-and-fix/README.md).

---

**1.** What is a "system of record"? Name AdmitFlow's for enquiries, enrolments and marketing consent.

**2.** When would you choose a file export over a webhook? When would you use both?

**3.** Why does a webhook signature cover the timestamp as well as the body?

**4.** A webhook receiver returns `500` for duplicate events. What happens next, and what should it return?

**5.** Explain the outbox pattern and why AdmitFlow uses it for messages.

**6.** A CRM `POST /contacts` times out. Why must you not simply retry it? What do you do instead?

**7.** OAuth 2.0 vs OpenID Connect: what does each answer?

**8.** Name four checks when verifying a Google ID token, and what goes wrong if you skip the audience check.

**9.** SSO is set up. How do leavers lose access, and what is SCIM for?

**10.** Why must an AI assistant over company documents filter by the user's permissions *before* retrieval results reach the model?

**11.** Name three design choices that make AdmitFlow's MCP server safe.

**12.** Shared database with `tenant_id`, or a database per client? Give one argument for each.

---

<details>
<summary><strong>Answers</strong></summary>

1. The authoritative source when systems disagree. Enquiries: AdmitFlow; enrolments: SIS; consent: CRM.
2. Files: when the source has no webhooks, for bulk/historical data, or when daily freshness is enough. Both: webhooks for speed, plus a periodic export to reconcile anything missed.
3. Otherwise an attacker could replay an old signed body with a fresh timestamp; signing both makes old requests detectably stale.
4. The sender retries repeatedly (and may eventually disable the webhook). Return `200` (e.g. `{"status": "duplicate"}`).
5. Record the intent to send in your own database (approved draft), and let a separate worker deliver, mark sent and retry failures. The request stays fast, nothing is lost when the provider is down, and only approved items can be sent.
6. The create may have succeeded; a retry can duplicate. Search by a natural key (email) first, link if found; use an idempotency key if the API supports one; otherwise stop and retry on the next run.
7. OAuth 2.0: may this app access this API on the user's behalf? OIDC: who is this user (identity via an ID token)?
8. Signature (JWKS), issuer, audience, expiry, `email_verified`, hosted domain. Without the audience check, ID tokens issued to *other* apps would be accepted by yours.
9. IT disables the account at the IdP; short AdmitFlow sessions expire. SCIM lets the IdP create, update and deactivate users in AdmitFlow automatically.
10. Once text is in the model's context it can appear in an answer; prompts can't reliably keep secrets. Permission filtering must happen in retrieval.
11. Acts as one named counsellor; only that counsellor's leads; same "not found" for hidden and missing leads; no send/update/delete tools; drafts need human approval; contact details omitted; inputs capped.
12. Shared: cheaper and simpler to operate. Separate: stronger isolation (one missing filter can't leak data) and often required by enterprise security reviews.

</details>
