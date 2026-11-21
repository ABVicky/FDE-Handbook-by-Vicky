# Lesson 03 — Webhooks done right

**Time:** ~3 hours · **Core**

## The problem

A webhook endpoint is a public URL that creates data in your system. Anyone on the internet can call it. It will receive duplicates (senders retry), old requests replayed by attackers, malformed bodies, and bursts of traffic.

## The five rules

1. **Verify the signature.** Sender and receiver share a secret; the sender signs each request.
2. **Reject old timestamps** to block replays.
3. **Be idempotent:** the same event processed twice has the same effect as once.
4. **Validate the payload** like any other input.
5. **Respond fast** (do slow work asynchronously), so the sender doesn't time out and retry.

## Signatures (HMAC)

AdmitFlow's scheme ([`integrations/webhooks.py`](../../../projects/admitflow/admitflow/integrations/webhooks.py)), the same shape Stripe and GitHub use:

```
X-AdmitFlow-Event-Id:  evt_9f2c41ab
X-AdmitFlow-Timestamp: 1790000000
X-AdmitFlow-Signature: sha256=<HMAC-SHA256(secret, "1790000000." + raw body)>
```

```python
def sign(secret, timestamp, body: bytes) -> str:
    mac = hmac.new(secret.encode(), f"{timestamp}.".encode() + body, hashlib.sha256)
    return "sha256=" + mac.hexdigest()

def verify(secret, timestamp, body, signature, now=None, tolerance=300):
    if not timestamp or not signature:
        raise WebhookError("missing signature headers")
    if abs((now or time.time()) - int(timestamp)) > tolerance:
        raise WebhookError("timestamp outside the allowed window (possible replay)")
    if not hmac.compare_digest(sign(secret, timestamp, body), signature):
        raise WebhookError("signature mismatch")
```

Details that matter:
- Sign the **raw bytes** of the body, before any JSON parsing (re-serializing changes bytes).
- Include the **timestamp** in what's signed, or an attacker could attach a fresh timestamp to an old body.
- Use **constant-time comparison** (`hmac.compare_digest`).
- Keep the secret in the secret manager; rotate it by accepting old and new secrets briefly during the change.

When integrating with a provider (Stripe, a CRM, a form builder), use **their** documented scheme and their SDK's verify function if one exists.

## Idempotency

Senders retry on timeouts and errors, so expect each event at least twice. AdmitFlow:
- derives the lead ID from the event ID (`WEB-evt_9f2c41ab`), so a redelivery maps to the same lead, and dedupe merges it
- records processed event IDs (`record_event`, backed by a primary key in SQL, so even two simultaneous deliveries can't both count as "first")
- answers redeliveries with `200 {"status": "duplicate"}`. Return **2xx** for duplicates, or the sender keeps retrying.

## Validation and error codes

| Situation | Response | Why |
| --- | --- | --- |
| Bad/missing signature, stale timestamp | `401` | Don't process; log for security review |
| Missing event ID | `400` | Can't be idempotent without it |
| Invalid payload (no name, no contact) | `422` | Sender's data problem |
| Not configured (no secret set) | `503` | Fail closed, never accept unsigned data |
| Processed / duplicate | `200` | Sender can stop retrying |

## Respond fast

Do the minimum in the request: verify, validate, store. Anything slow (notifying a counsellor, CRM sync, AI drafting) happens afterwards, through background work or the outbox (Lesson 02). Many senders time out after 5–10 seconds.

## Testing webhooks

```python
def post_form(client, payload, event_id="evt_0001abcd", secret=SECRET):
    body = json.dumps(payload).encode()
    ts = str(int(time.time()))
    headers = {"X-AdmitFlow-Timestamp": ts, "X-AdmitFlow-Signature": sign(secret, ts, body),
               "X-AdmitFlow-Event-Id": event_id, "Content-Type": "application/json"}
    return client.post("/public/webhooks/website-form", content=body, headers=headers)

def test_redelivered_event_is_idempotent(api, repo):
    post_form(api, FORM)
    assert post_form(api, FORM).json() == {"status": "duplicate"}
    assert repo.list_leads(search="zoe.garcia")[1] == 1
```

See [`tests/test_integrations.py`](../../../projects/admitflow/tests/test_integrations.py) for the full set: wrong secret, replayed timestamp, bad event ID, invalid forms, unconfigured.

## Check yourself

Write a small script that plays the website: it signs and sends five submissions to your running API, including one sent twice and one with a tampered body. Check the responses and the resulting leads.

Next: [Lesson 04 — Calling third-party APIs reliably](04-calling-third-party-apis.md)
