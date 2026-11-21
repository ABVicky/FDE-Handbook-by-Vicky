# Lesson 07 — Incidents: response, communication and learning

**Time:** ~3 hours · **Core**

## Why this matters

Something will go wrong in production. Clients remember **how you handled it** more than the fact that it happened: how quickly they heard from you, whether you were honest, and whether it happened again.

## During an incident

1. **Acknowledge** quickly: tell the client you know and you're on it, before you understand it.
2. **Mitigate first, diagnose second:** roll back, switch to the fallback engine, restart. Restore service, then find the root cause.
3. **One person coordinates** (even if it's you alone: write things down).
4. **Keep a timeline** as you go: times, observations, actions.
5. **Communicate on a schedule:** every 30–60 minutes for a major incident, even if there's no news.
6. **Declare it over** when users are unaffected, and say what's still to do.

## Severity levels (agree them with the client)

| Severity | Example | Response |
| --- | --- | --- |
| **SEV1** | AdmitFlow down during an intake deadline; data exposed | Immediately, any hour; client leadership informed |
| **SEV2** | Messages not sending; assistant giving wrong fees | Within 1 hour in working hours |
| **SEV3** | Slow reports; one feature broken | Next working day |

A suspected **data breach** has extra obligations: involve the client's privacy lead immediately; many laws have strict notification deadlines.

## Communicating

To non-technical stakeholders: **what's affected, since when, what we're doing, when they'll hear next.** No jargon, no guesses presented as facts.

> **10:40** WhatsApp follow-ups have not been sending since Monday afternoon. Email is fine. We've found the cause (an expired access key) and expect to fix it within 30 minutes. Next update 11:15.

## After the incident: blameless reviews

Write an [incident report](../../../templates/incident-report.md) within two working days:
- **Blameless:** "the token expired and nothing alerted us," not "Priya forgot to renew the token." People make mistakes; systems should catch them.
- **Contributing factors:** why it happened *and* why it wasn't detected sooner.
- **Actions** with owners and dates: prevent, detect, mitigate. Then actually do them, and check in a month.

The [break & fix](../break-and-fix/README.md) is a complete example: six contributing factors, each with a fix.

## Runbooks

A runbook turns 2am panic into a checklist: for each alert, what it means, first checks, likely causes, fixes and who to tell. AdmitFlow's: [`docs/runbook.md`](../../../projects/admitflow/docs/runbook.md). Every incident should improve it.

## Game days

Practise before it's real: break something on purpose in staging (stop the database, revoke a token, fill the disk) and run the response with the team. You'll find missing alerts, wrong runbook steps and access problems while the stakes are low.

## Check yourself

Do the break & fix, then the [Field Track](../field-track.md) game day.

Next: [Lesson 08 — Backups, disaster recovery and compliance](08-backups-and-compliance.md)
