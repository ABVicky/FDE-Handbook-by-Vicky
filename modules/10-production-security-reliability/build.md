# Module 10 Build — AdmitFlow, hardened

**Time:** ~25 hours · **Capabilities:** C4

## Scenario

AdmitFlow is about to handle the September intake: thousands of enquiries, a public assistant on the website, and messages going out daily. Mr. Okafor's go-live conditions: *"Show me how you'd know it's broken before a parent tells us, how you'd recover the data, and who can see what."*

## Requirements

1. **Threat model** (Exercise 01) with the top risks tested
2. **Abuse protection:** rate limits on `/public/*` (per IP) and login (per username), `429` with `Retry-After`; input caps; security headers on every API response; CSP on the dashboard
3. **Data protection:** a log filter masking emails and phones (without masking dates and IDs); AI drafts get first names only and redacted notes; a written retention policy (Exercise 02 implements it)
4. **Audit log:** append-only table and migration; events for logins (success/failure/rate-limited), SSO, assignments, status changes, draft decisions, webhook-created leads; `GET /audit` for admins
5. **Observability:** `/metrics` (Prometheus format, token-protected) with request counts and latency by route template, outbox sent/failed and oldest-waiting gauge, assistant answered/declined, failed logins; alert rules with runbook links
6. **Backups:** `admitflow backup` + `verify-backup` (SQLite) and the PostgreSQL procedure; one restore drill recorded
7. **Runbook** with SLOs, one section per alert, and procedures (backup, restore drill, secret rotation, offboarding)
8. **Tests** for every control above

## Running the reference solution

```bash
export ADMITFLOW_METRICS_TOKEN=$(python -c 'import secrets; print(secrets.token_urlsafe(24))')
```

```bash
admitflow serve
```

```bash
curl -s -H "Authorization: Bearer $ADMITFLOW_METRICS_TOKEN" http://localhost:8000/metrics | head
```

```bash
DATABASE_URL=sqlite:///admitflow.db admitflow backup --to backups/admitflow-$(date +%F).db
```

Environment: `ADMITFLOW_PUBLIC_RATE_PER_MINUTE` (default 30), `ADMITFLOW_LOGIN_RATE_PER_MINUTE` (default 5), `ADMITFLOW_METRICS_TOKEN`.

## Done when

- [ ] All requirements implemented and tested
- [ ] The break & fix replay shows your alert firing within 2 hours of the token expiring
- [ ] Restore drill recorded in the runbook
- [ ] Mr. Okafor (a peer) walks through the runbook and can answer: "the outbox alert fired at 2am, what do I do?"

## Stretch

- OpenTelemetry tracing across API → retrieval → LLM → database, viewed in a local Jaeger or Grafana Tempo
- Stop retrying on 401/403 in the outbox and alert immediately (from the incident report)
- Restrict lead *reads* to assigned counsellors, if the client confirms that's the policy (see the Exercise 01 answer)
- A Locust load test with a written capacity statement
