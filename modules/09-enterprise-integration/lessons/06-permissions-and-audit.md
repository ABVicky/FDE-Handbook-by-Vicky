# Lesson 06 — Permissions, multi-tenancy and audit

**Time:** ~3 hours · **Core**

## Authorization models

| Model | Idea | AdmitFlow |
| --- | --- | --- |
| **RBAC** (role-based) | Permissions come from roles | `counsellor`, `admin` |
| **Ownership / row-level** | You can act on records you own | Counsellors change only leads assigned to them (or unassigned) |
| **ABAC** (attribute-based) | Rules over attributes ("same campus", "office hours") | A later extension: campus-scoped counsellors |

Most real systems combine RBAC with row-level rules. Write the rules in **one place**, test each one, and **deny by default**.

## Respecting the source system's permissions

When you pull data from another system, you inherit its access rules. If a hospital's document system says only senior staff can read HR policies, your AI assistant must enforce the same rule. That means:
- import the **permissions** with the data (who/which groups can see each record)
- **filter at query time** by the current user's identity, before anything reaches a model or a screen
- re-sync permissions regularly; access changes as people change roles

Copying data without its permissions is one of the most common enterprise integration security failures.

## Least privilege for integrations and AI tools

AdmitFlow's MCP server acts **as one named counsellor**, sees only that counsellor's leads, returns the same "not found" for leads that exist but aren't theirs (so it doesn't reveal what exists), omits contact details, and has no tools that send or modify. Apply the same thinking to every service account and token.

## Multi-tenancy

If you'll serve several clients from one deployment (a second institute wants AdmitFlow), choose how to isolate them:

| Approach | Isolation | Cost / effort |
| --- | --- | --- |
| Separate deployment per client | Strongest | Highest operational cost |
| Separate database per client | Strong | Medium |
| Shared database, `tenant_id` on every row | Weakest; one missing filter leaks data | Lowest |

With a shared database, enforce the tenant filter centrally (repository layer, or PostgreSQL **row-level security**), and test cross-tenant access explicitly. Many enterprise clients will require separate deployments or databases; ask early.

## Audit logs

Security reviews will ask: **who did what, when?** Log security-relevant events:
- sign-ins (success and failure), role changes, user creation and removal
- assignments, status changes, exports
- draft approvals and rejections (AdmitFlow stores `decided_by`, `decided_at`)
- integration actions (what was sent, synced, imported)

Audit logs should be **append-only** (nobody edits history), kept for an agreed period, and contain identifiers rather than full personal data. Module 10 adds structured audit logging.

## Data migration

Moving data from an old system into a new one is its own project:
1. **Map** fields and values (old statuses → new statuses)
2. **Profile** the old data: duplicates, blanks, invalid values
3. **Dry-run** into a copy; reconcile counts and spot-check records with users
4. **Cut over** with a freeze window, a final delta load, and a rollback plan
5. **Keep** the old system read-only for a while

AdmitFlow's pipeline habits (idempotent loads, rejected-row reports, reconciliation) are exactly what a migration needs.

## Check yourself

A second institute will use AdmitFlow. Write a one-page proposal for tenant isolation: which approach, what changes in the code (every table, query, token, background job, and the MCP server), how you'd test that institute A can never see institute B's leads, and what you'd tell each client's security team.

Next: [Lesson 07 — Enterprise platforms: CRM, ERP, ITSM and data platforms](07-enterprise-platforms.md)
