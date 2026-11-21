# Deployment Guide — <System name>

**Environment:** staging / production · **Owner (client side):** · **Owner (engineering):** · **Last updated:**

## 1. Overview
<What is deployed, where, and a diagram. Link the technical design.>

## 2. Prerequisites
- Accounts and roles needed (who grants them)
- Tools and versions (CLI, Docker, Terraform…)
- Network access (VPN, allow-listed IPs)

## 3. Configuration
| Variable / secret | Purpose | Where it's stored | Who can change it |
| --- | --- | --- | --- |

## 4. First-time setup
Step-by-step, copy-pasteable, one command per step, each with what success looks like.

## 5. Releasing a new version
1. CI green on the commit
2. Back up the database (or confirm the automatic backup is recent)
3. Run migrations
4. Deploy
5. Smoke test: `/health`, `/ready`, log in, open a lead
6. Announce to users (if visible changes)

## 6. Rolling back
How to return to the previous version, and what to do about database changes.

## 7. Scheduled jobs
| Job | Schedule | What it does | Where to see its result |
| --- | --- | --- | --- |

## 8. Backups and restore
Where backups are, how long they're kept, **date of the last successful test restore**.

## 9. Go-live checklist
- [ ] HTTPS only; certificates auto-renew
- [ ] Secrets in a secret manager, none in code or images
- [ ] Least-privilege service accounts
- [ ] Backups on **and a restore tested**
- [ ] Monitoring and alerts (link the runbook)
- [ ] Budget alerts set
- [ ] CORS and allowed origins limited to real domains
- [ ] Rollback tested
- [ ] Client-side owner named and trained

*Worked example: [AdmitFlow deployment](../projects/admitflow/deploy/README.md)*
