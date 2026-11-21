# Exercise 02 — A retention job that anonymizes old leads

Policy agreed with the client: leads with **no activity for 24 months** that **didn't enrol** are anonymized: name becomes "Former enquirer", contact details and notes are removed, course and channels are kept (for reports), and each change is audited.

Write `purge_inactive(repo, now, months=24, apply=False)`:
- "Activity" = the latest of the lead's received time and its notes' times
- Dry run by default: return what *would* change
- With `apply=True`: anonymize, and write one audit event per lead (`retention.anonymize`, no personal data in the event)
- Never touch enrolled leads
- Safe to run twice
