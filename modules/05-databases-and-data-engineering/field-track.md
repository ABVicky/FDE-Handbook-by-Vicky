# Module 05 — Field Track: Ask for data access the right way

**Time:** ~1.5 hours · **Capabilities:** C1, C5

## Why

On real engagements, **data access is the most common critical-path delay**. FDEs wait days or weeks for exports, database credentials, firewall rules and approvals. A clear, specific, security-conscious request gets approved faster, and builds trust with the people who'll decide whether your system goes live.

## The task

AdmitFlow needs a regular admissions feed from the institute's student information system (SIS), which runs on an old server in the office (Mr. Okafor maintains it). Write the email you'd send to Mr. Okafor, copying Mr. Fernandes, in `my-work/field-track/m05-data-access-request.md`.

It must cover:

1. **Purpose:** why you need it, in business terms (which decision it supports)
2. **Exactly what:** the fields you need, and the ones you **don't** (data minimization). Do you need `fee_paid`? Date of birth? Home address?
3. **How often and how:** e.g. a weekly CSV export to a shared folder; or read-only database access; or an API. Offer options, from least to most effort for him, and say which you recommend.
4. **Minimum access:** read-only; specific tables or views only; a dedicated service account, not a personal login
5. **Protection:** where the data will be stored, encrypted in transit and at rest, who can see it, retention period, and deletion on request
6. **What you'll give back:** e.g. the unmatched-admissions list (data quality feedback for his system)
7. **A specific ask with a date:** "Could we have a 20-minute call on Thursday to choose an option?"

## Rules

- ≤ 250 words in the email body (attach detail if needed)
- No jargon he wouldn't use; no blame for the old system
- Assume he's busy and cautious, and that he's right to be cautious

## Done when

- [ ] All seven points covered
- [ ] Lists fields you deliberately **won't** take
- [ ] Offers at least two delivery options with a recommendation
- [ ] Read by someone else, who could say in one sentence what you're asking for
