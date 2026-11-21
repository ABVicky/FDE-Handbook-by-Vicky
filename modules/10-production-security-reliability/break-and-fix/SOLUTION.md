# Break & Fix — Solution

> ⚠️ Try it properly first.

## What happened

At **Monday 14:00** the WhatsApp provider access token expired. From then on every WhatsApp send failed with `HTTP 401: access token has expired`. The outbox behaved as designed: it left the drafts `approved` and retried them every hour, so 30 follow-ups (every WhatsApp message approved after 14:00) waited three days. Email kept working, which made the system look healthy.

## Why nobody noticed (contributing factors)

| # | Gap | Fix |
| --- | --- | --- |
| 1 | **No alert on what students experience.** Nothing measured how long approved messages waited | `admitflow_outbox_oldest_approved_minutes` + `AdmitFlowOutboxStuck` alert (> 30 min) |
| 2 | **The scheduler ignored the job's exit code** (`send-approved` returns 1 when sends fail) | Scheduler marks the job failed and notifies on non-zero exit; plus `AdmitFlowOutboxFailures` |
| 3 | **1,125 warnings in a log nobody reads.** Logs are for investigating, not for detecting | Alerts on metrics; logs searched during the incident |
| 4 | **A credential with an expiry date and no owner reminder** | Credential inventory with expiry dates; reminder 30 days before; prefer non-expiring system-user tokens where the provider allows, rotated deliberately |
| 5 | **Retrying a permanent error.** A 401 won't fix itself, but it was treated like a temporary failure | Classify errors: on 401/403, stop retrying that channel and raise an alert immediately |
| 6 | **The dashboard showed "approved", which counsellors read as "sent"** | Show "approved, not yet sent (waiting 3 h)" in the UI |

With the alert from [`deploy/monitoring/alerts.yml`](../../../projects/admitflow/deploy/monitoring/alerts.yml):

```bash
python solution/with_alert.py
```

```
token expired:      Mon 14:00
alert first fired:  Mon 15:00  (1 h later)
```

## First 30 minutes on Thursday

1. Acknowledge the incident; tell Mr. Fernandes you're on it (2 minutes, before investigating).
2. `admitflow send-approved --dry-run`, then a real run: read the failure reason (401, expired token).
3. Generate a new token at the provider; store it in the secret manager; restart/redeploy the job.
4. Run `send-approved` once by hand. **Before** that, decide with Mr. Fernandes whether three-day-old messages should go out as written. Some may now be wrong ("see you at the campus visit tomorrow"). Usually: counsellors review and re-approve, or send a short apology plus the original content.
5. Confirm `admitflow_outbox_oldest_approved_minutes` is back to 0.
6. List affected students (drafts approved after Monday 14:00 that were sent late) for the follow-up.

## Sample incident report (abridged)

> **Summary.** From Monday 14:00 to Thursday 11:05, WhatsApp follow-ups approved in AdmitFlow were not sent because the provider token expired. 30 students received no reply for up to 3 days. Email follow-ups were unaffected.
> **Detection.** A parent's phone call on Thursday 10:15. No automated alert existed for unsent messages.
> **Root cause.** An expiring provider token with no renewal reminder; the scheduled job's failures were logged but not alerted on, and the scheduler ignored its exit code.
> **Actions.** (1) Alert when approved messages wait > 30 minutes: *done*. (2) Stop retrying 401/403 and alert immediately: FDE, Friday. (3) Credential inventory with expiry reminders: Mr. Okafor, next week. (4) Show "not yet sent" in the dashboard: FDE, next sprint. (5) Counsellors call the 30 affected students today: Mr. Fernandes.

## Message to Mr. Fernandes

> WhatsApp follow-ups stopped sending on Monday afternoon because the provider's access key expired, and our system didn't alert anyone. It's fixed and the messages are ready to go. Before sending them, could counsellors check the 30 affected students' messages in case anything is now out of date? I've added an alert so this would now be caught within an hour, and I'll send you the full report by Monday.

## The general lesson

Monitor what users experience (*"are approved messages reaching students?"*), not just whether processes run. An alert that fires in an hour beats a thousand log lines.
