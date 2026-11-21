# Lesson 06 — Reliability patterns

**Time:** ~3 hours · **Core**

## Everything fails eventually

Databases restart, providers have outages, networks drop packets, tokens expire. Reliable systems assume failure and decide in advance what happens.

## The patterns

| Pattern | What | AdmitFlow |
| --- | --- | --- |
| **Timeouts** | Never wait forever | HTTP clients: 10–20 s; LLM calls bounded |
| **Retries with backoff** | Retry *transient* failures, with growing waits and a cap | CRM reads/updates; httpx calls |
| **Don't retry the permanent** | 400/401/403 won't fix themselves | Lesson from the incident: stop on 401 and alert |
| **Idempotency** | Safe to repeat | Webhooks, CRM sync, imports, outbox |
| **Graceful degradation** | Keep the core working when a part fails | No model → offline assistant; no scorer → 503 on scoring only |
| **Circuit breaker** | After repeated failures, stop calling a dependency for a while | *Stretch:* around the LLM provider |
| **Bulkheads** | Isolate parts so one can't exhaust shared resources | Outbox runs as a separate job, not inside API requests |
| **Health checks** | Liveness vs readiness (Module 06) | `/health`, `/ready` |
| **Queues / outbox** | Absorb bursts and outages | Approved drafts wait in the outbox |

## Graceful degradation, concretely

Decide for each dependency: **what do users see when it's down?**

| Dependency down | User experience |
| --- | --- |
| Database | API not ready (`503`); dashboard shows "AdmitFlow is temporarily unavailable" |
| LLM provider | Assistant falls back to the offline engine; drafts use the template |
| Lead-scoring model | Priority list unavailable; everything else works |
| WhatsApp provider | Drafts stay approved; outbox alert fires; email unaffected |
| CRM | Sync fails and reports; nothing else affected |
| Google sign-in | Admin break-glass password login |

## Load testing

Find limits before users do. Simulate realistic traffic (e.g. with Locust or k6) against **staging**, with production-like data volume (Module 05's big database):

- 6 counsellors clicking through leads, plus a burst of 200 assistant questions per minute after an ad goes out
- watch p95 latency, error rate, database CPU and connections

Then you can tell the client: "the current setup handles about N requests per second; beyond that, add instances or a larger database tier."

## Capacity and database connections

Each API instance holds a pool of database connections. 3 instances × 10 connections = 30; a small managed database may allow only 25. Set pool sizes and `max_instances` together, or scaling up during a traffic spike will *cause* an outage.

## Check yourself

Write a Locust (or k6) script with two user types: a counsellor (log in, list leads, open one, add a note) and a public visitor (ask the assistant). Run it against a local deployment, find the request rate where p95 exceeds 500 ms, and note what limits you first: CPU, database or something else.

Next: [Lesson 07 — Incidents: response, communication and learning](07-incidents.md)
