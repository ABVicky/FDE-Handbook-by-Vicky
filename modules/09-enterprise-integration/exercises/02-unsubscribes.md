# Exercise 02 — A CRM-owned field: unsubscribes

Marketing manages consent in the CRM. When a student unsubscribes there, AdmitFlow must never send them follow-up messages.

1. Decide the **system of record** for consent and write the field-ownership table.
2. Design the change: where `unsubscribed` lives in AdmitFlow, how it's read from the CRM, how often, and what the outbox does with it.
3. Write tests first (using the `FakeCrm` pattern): (a) the sync reads the flag and never overwrites it; (b) the outbox skips approved drafts for unsubscribed leads, with a reason; (c) a new website enquiry from an unsubscribed student does **not** clear the flag.
4. Implement it, including an Alembic migration.
5. What should a counsellor see in the dashboard for an unsubscribed lead?
