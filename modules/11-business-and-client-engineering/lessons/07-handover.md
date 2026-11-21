# Lesson 07 — Handover and post-deployment support

**Time:** ~3 hours · **Core**

## Why

An FDE's work is judged a year later: is the system still running, still used, still improving? If it collapses when you leave, the engagement failed, however good the code was. Plan the handover from the first week.

## Who owns what after you leave

Agree it explicitly:

| Area | Owner at the client | Backup | What they need |
| --- | --- | --- | --- |
| Day-to-day use, training new staff | Mr. Fernandes (and Priya as champion) | — | User guide, training material |
| Accounts and access | Mr. Okafor | Mr. Fernandes | Runbook: offboarding, roles |
| Operations (alerts, backups, restarts) | Mr. Okafor | FDE support contract | Runbook, dashboards, access |
| Course documents for the assistant | Admissions office | Mr. Fernandes | How to update and re-run the evaluation |
| Code changes | Vendor / future developer | — | README, ADRs, tests, CI |
| Budget and vendor contracts | Ms. Chen | — | Cost estimate and actuals |

## The handover pack

1. **User guide** for counsellors and reception ([template](../../../templates/user-guide.md)): task-based ("add a phone enquiry"), with screenshots, one page per task
2. **Handover document** ([template](../../../templates/handover.md)): what exists, who owns what, how to get help, known issues, the roadmap
3. **Runbook** (Module 10) and **deployment guide** (Module 06)
4. **Architecture and decisions:** technical design + ADRs
5. **Access:** every credential transferred to client-owned accounts; yours removed
6. **Recorded walkthroughs:** 10-minute videos for the most common tasks

AdmitFlow's examples: [`docs/user-guide.md`](../../../projects/admitflow/docs/user-guide.md), [`docs/handover.md`](../../../projects/admitflow/docs/handover.md).

## Training that sticks

- Short sessions per role, hands-on with their own data
- A one-page quick reference per role
- "Train the trainer": the champion can onboard new staff without you
- A check after two weeks: can each person do the five core tasks unaided?

## Post-deployment support

Agree a support model before go-live: how issues are reported (one channel, not WhatsApp messages to the FDE's personal phone), response times by severity, what's included, and when it ends. A **hypercare** period (2–4 weeks of close support after go-live) catches adoption problems while they're small.

## Measuring impact, and closing

At the end of the engagement:
- Report the outcome against the agreed metrics (the 24-hour contact rate, enrolments by channel), honestly
- Capture **lessons learned** with the client
- Write up **reusable assets** for your own organization: connectors, templates, patterns (FDEs feed the product, Module 01)
- Agree what happens next: support, phase 2, or a clean exit

## Check yourself

Write AdmitFlow's handover document using the template, then ask someone who has never seen AdmitFlow to answer, from the documents alone: "The outbox alert fired. What do you do?" and "A new counsellor starts Monday. What do they need?"

Next: [Exercises](../exercises/README.md) and the [build](../build.md).
