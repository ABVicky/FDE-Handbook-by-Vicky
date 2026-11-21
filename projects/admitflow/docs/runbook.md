# AdmitFlow Runbook

**Service owner (institute):** Mr. Okafor (IT) · **Engineering contact:** <FDE name, phone> · **Escalation:** Mr. Fernandes (business impact decisions)
**Last reviewed:** Module 10 · Review this runbook every quarter and after every incident.

## Service level objectives (SLOs)

| SLI | Objective | Measured by |
| --- | --- | --- |
| Availability: share of API requests that don't fail with 5xx | **99.5%** per calendar month (≈ 3.6 hours of failures allowed) | `admitflow_http_requests_total` |
| Latency: GET /leads | **95%** of requests under **500 ms** | `admitflow_http_request_seconds` |
| Message delivery: approved follow-ups sent | **99%** within **15 minutes** of approval | `admitflow_outbox_oldest_approved_minutes`, outbox logs |
| Assistant: fee answers correct | **100%** on the evaluation set before every release | `admitflow eval-assistant` in CI |

Counsellors work 9am–7pm; incidents outside those hours are fixed next morning unless messages are stuck before an intake deadline.

## Quick reference

| Task | Command / place |
| --- | --- |
| Is it up? | `curl -fsS https://<api>/health` and `/ready` |
| Logs | `docker compose logs -f api` (VM) or the cloud console's log viewer (search by `request_id=`) |
| Metrics | `/metrics` with `Authorization: Bearer $ADMITFLOW_METRICS_TOKEN`, or the Grafana dashboard |
| Restart | `docker compose restart api` (VM) or redeploy the current revision (cloud) |
| Roll back | Previous image / revision: see [deploy/README.md](../deploy/README.md#3-rolling-back) |
| Audit trail | `GET /audit` as an admin |

## Alerts

### API down
1. Check `/health` from outside the network and from the server itself (networking vs. process).
2. `docker compose ps` / cloud service status: is the container running? Restarting in a loop?
3. Read the last 100 log lines for the startup error (missing secret, database unreachable).
4. If a deploy just happened: **roll back first**, investigate after.

### High error rate
1. Find the failing route: `admitflow_http_requests_total{status=~"5.."}` by `route`.
2. Search logs for the error and its `request_id`.
3. Common causes: database unavailable (`/ready` = 503), a bad deploy, an external dependency (LLM provider) failing. The offline assistant engine can be forced with `ADMITFLOW_LLM=offline`.

### Slow requests
1. Which route? Check database CPU and slow-query log.
2. Look for a missing index or an N+1 pattern (Module 05). `EXPLAIN ANALYZE` the slow query.
3. Short-term: scale the API up (more instances); long-term: fix the query.

### Outbox stuck
Approved follow-ups aren't being sent: students are waiting.
1. Run `admitflow send-approved --dry-run` to see what's queued; then without `--dry-run` and read the failure reasons.
2. Typical causes: **expired or revoked provider token** (WhatsApp/SMTP), provider outage, missing sender configuration, the scheduler not running the job.
3. Rotate the credential in the secret manager, redeploy/restart the job, run `send-approved` once by hand, confirm `admitflow_outbox_oldest_approved_minutes` drops to 0.
4. Tell Mr. Fernandes how many students were delayed and for how long.

### Suspicious traffic
1. Which accounts or IPs? Check `GET /audit?action=auth.login.failed` and logs for `429`.
2. If one account is targeted: confirm with the person; reset their password (or rely on Google SSO).
3. If the public assistant is being scraped: lower `ADMITFLOW_PUBLIC_RATE_PER_MINUTE` or block at the gateway/WAF.

### Assistant declining
1. Run `admitflow eval-assistant`: did correctness drop?
2. Check `data/course_docs` in the deployed image: missing or mis-tagged (`superseded: true`) documents?
3. If using Claude: check provider status and refusal/fallback rates in logs.

## Procedures

### BACKUP
- **PostgreSQL (production):** managed automated backups with point-in-time recovery (7+ days). Additionally, weekly logical backup: `pg_dump --format=custom --file=admitflow-$(date +%F).dump "$DATABASE_URL"`, stored in a separate account or bucket with restricted access.
- **SQLite (pilot):** `admitflow backup --to /backups/admitflow-$(date +%F).db` (consistent online copy, verified automatically).

### RESTORE DRILL (quarterly; record the date below)
1. Restore the latest backup into a **new** database (never over production).
2. Point a staging API at it (`DATABASE_URL=…`) and run `alembic current` and `admitflow verify-backup` (SQLite) or row counts (PostgreSQL).
3. Log in, open a lead, check its notes.
4. Record: date, backup used, time taken, problems found.

| Date | Backup | Duration | Result |
| --- | --- | --- | --- |
| | | | |

### ROTATE A SECRET
1. Create the new value in the secret manager (new version).
2. For the session signing key: deploying a new `ADMITFLOW_SECRET_KEY` logs everyone out; do it outside working hours.
3. For provider tokens: update, redeploy or restart, run a smoke test (`send-approved --dry-run`, `crm-sync` on staging).
4. Revoke the old value at the provider. Record in the audit notes.

### OFFBOARD A STAFF MEMBER
1. IT disables their Google account (sessions end within 8 hours).
2. Reassign their leads (admin: `PATCH /leads/{id}`) and remove their AdmitFlow user.
3. If they held any integration credentials, rotate them.

## After every incident
Write an [incident report](../../../templates/incident-report.md) within two working days: blameless, with a timeline, impact, root cause, and actions with owners and dates.
