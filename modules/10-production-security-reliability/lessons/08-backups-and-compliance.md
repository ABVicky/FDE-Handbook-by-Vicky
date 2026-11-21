# Lesson 08 — Backups, disaster recovery, audit and compliance

**Time:** ~3 hours · **Core**

## RPO and RTO

Two numbers to agree with the client:
- **RPO** (recovery point objective): how much data can you afford to lose? ("At most the last hour.")
- **RTO** (recovery time objective): how long can you be down? ("Back within 4 hours during an intake.")

They decide the backup design. A managed database with point-in-time recovery gives an RPO of minutes; a nightly dump gives up to 24 hours.

## Backups

AdmitFlow's approach (runbook: BACKUP):
- **PostgreSQL:** the managed service's automated backups with point-in-time recovery, plus a weekly `pg_dump` stored in a **separate account or bucket** (so one compromised account can't delete both).
- **SQLite (pilot):** `admitflow backup --to …` uses SQLite's online backup API, which is safe while the app runs (copying the file mid-write can produce a corrupt copy), then verifies the copy:

```bash
admitflow backup --to /backups/admitflow-2026-11-21.db
```

```
backed up to /backups/admitflow-2026-11-21.db
integrity: ok
  audit_log        124
  leads            190
  …
```

## A backup you haven't restored is a hope

Run a **restore drill** every quarter (runbook: RESTORE DRILL): restore into a new database, point a staging API at it, log in, open a lead, and record the date and how long it took. The test `test_backup_and_verify` does a miniature version on every CI run: back up, then open the copy with the application and read the leads.

## Disaster recovery

What if the whole region, account or provider is unavailable? For AdmitFlow's size, a reasonable plan is:
1. Backups replicated to a second region
2. Infrastructure described as code or step-by-step docs (Module 06), so it can be rebuilt
3. A tested procedure with a realistic RTO ("a day"), agreed with the client

Large clients may require warm standby or multi-region deployments, at significant cost. Make the trade-off explicit.

## Audit logs

AdmitFlow records security-relevant actions in an append-only `audit_log` table ([`db.py`](../../../projects/admitflow/admitflow/db.py) `AuditRow`): logins (success, failure, rate-limited), SSO logins, lead assignments and status changes, draft approvals and rejections, and webhook-created leads. Admins read it via `GET /audit`.

To make "append-only" real, the application's database user should have `INSERT` and `SELECT` on `audit_log` but not `UPDATE` or `DELETE`:

```sql
REVOKE UPDATE, DELETE ON audit_log FROM admitflow_app;
```

Agree a retention period, and keep audit logs out of reach of the people whose actions they record.

## Compliance, briefly

Clients may ask about:
- **Data-protection law** (GDPR, India's DPDP Act, and others): lawful basis, minimization, rights to access and deletion, breach notification. The client's privacy team decides policy; you implement and document it.
- **SOC 2 / ISO 27001**: frameworks for an organization's security controls. As an FDE you'll often provide **evidence**: access reviews, change history (Git + CI), backup tests, incident reports. Everything in this module produces that evidence.
- **Sector rules** (health, finance, education) with their own requirements.

You don't need to be a compliance expert. You need to build systems that make the evidence easy to show.

## Check yourself

Do a full restore drill for your deployment (SQLite or PostgreSQL), time it, and fill in the runbook's drill table. Then write two sentences for Ms. Chen: what our RPO and RTO actually are today, and what it would cost to halve each.

Next: [Exercises](../exercises/README.md) and the [build](../build.md).
