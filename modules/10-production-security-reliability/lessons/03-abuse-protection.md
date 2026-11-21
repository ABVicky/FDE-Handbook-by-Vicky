# Lesson 03 — Protecting against abuse: rate limits, input limits and browser security

**Time:** ~3 hours · **Core**

## Rate limiting

Public and login endpoints attract bots: credential stuffing, scraping, cost attacks on AI endpoints. A **token bucket** allows short bursts and a steady rate ([`security.py`](../../../projects/admitflow/admitflow/security.py)):

```python
class RateLimiter:
    def __init__(self, rate_per_minute, burst): ...
    def allow(self, key, now=None) -> (bool, retry_after_seconds): ...
```

AdmitFlow's limits:

| Endpoint | Key | Default | On limit |
| --- | --- | --- | --- |
| `/public/*` (assistant, webhook) | Client IP | 30/min, burst 10 | `429` + `Retry-After` |
| `/auth/login` | Username | 5/min, burst 5 | `429`, audited `auth.login.rate_limited` |

Limiting login **by username** stops guessing one account's password from many IPs; limiting **by IP** stops one source hammering many accounts. Production systems often do both.

**Caveats you must know:**
- This limiter is **in memory, per process**. With 3 API instances, the effective limit is 3×. For a global limit use a shared store (Redis) or, better, the platform's **API gateway / WAF** rate limiting.
- Behind a proxy or load balancer, `request.client.host` is the proxy's IP. Configure trusted proxy headers (`X-Forwarded-For`) carefully, or every user shares one bucket. Uvicorn's `--proxy-headers --forwarded-allow-ips` does this.

## Input limits

Every input has a maximum: question ≤ 500 characters, notes ≤ 2,000, page size ≤ 100, webhook body validated. Limits protect against memory exhaustion, slow queries and, for LLM features, **cost**: a 100,000-character "question" costs real money per request.

For AI endpoints, also set a **spending limit** at the provider and a budget alert (Module 08, Lesson 08).

## Security headers

Added to every API response by middleware:

| Header | Purpose |
| --- | --- |
| `Strict-Transport-Security` | Browsers use HTTPS only, for a year |
| `X-Content-Type-Options: nosniff` | Don't guess content types (prevents some injection tricks) |
| `X-Frame-Options: DENY` / CSP `frame-ancestors 'none'` | Can't be embedded in another site (clickjacking) |
| `Referrer-Policy: no-referrer` | Don't leak URLs to other sites |
| `Cache-Control: no-store` | Never cache responses containing personal data |

The dashboard's nginx config adds a **Content-Security-Policy** (`default-src 'self'; script-src 'self'; …`): the browser refuses to run scripts from anywhere else, which turns many XSS bugs into harmless ones. Tighten `connect-src` to the real API URL in production.

## CORS, CSRF and XSS: a quick recap

- **CORS** (Module 04): allow only the real dashboard origin.
- **CSRF**: AdmitFlow sends tokens in the `Authorization` header (not cookies), so browsers don't attach them automatically, and classic CSRF doesn't apply. If you switch to cookies, add CSRF protection and `SameSite` cookies.
- **XSS**: React escapes output; never use `dangerouslySetInnerHTML` with data; CSP as a second layer.

## Abuse of AI features specifically

- **Prompt injection** can't be rate-limited away; it's handled by design (Module 08).
- **Cost abuse:** rate limits + input caps + provider spending limits + an alert on unusual question volume.
- **Content abuse:** someone uses the public assistant to generate off-topic content. Grounding (answer only from documents, otherwise "I don't know") largely prevents this.

## Check yourself

Put the API behind a reverse proxy locally (Caddy or nginx). Without proxy-header configuration, show that all requests appear to come from one IP and share one rate-limit bucket; then fix it. Write down what you'd configure on your cloud platform instead.

Next: [Lesson 04 — Security testing](04-security-testing.md)
