# Module 10 — Production Engineering, Security and Reliability

> **In plain words:** A working app isn't the same as a trustworthy one. Here you'll learn to protect people's data, notice problems before users do, and recover calmly when something breaks, because something always does.
>
> **What you'll build:** A hardened AdmitFlow: protection against abuse, an activity log, alerts when things go wrong, tested backups, and a step-by-step guide for emergencies.
>
> **You can skip for now:** Load testing and tracing (stretch).
>
> **Comes after:** [Module 09: Enterprise Systems and Integration](../09-enterprise-integration/README.md) · **Leads to:** [Module 11: Business and Client Engineering](../11-business-and-client-engineering/README.md)
>
> **How to work through it:** read the lessons in order → try the exercises → do the build → do the break & fix → do the Field Track → tick the "Done when" list. New here? Read [Start Here](../../START-HERE.md) first.

**Stage:** 4 — Field-ready · **Time:** ~3 weeks at 15–20 h/week · **Builds:** C4 (Deploy and integrate)
**Prerequisites:** [Module 09](../09-enterprise-integration/README.md).

## Outcome

After this module you can turn a working demo into a system a business can trust: threat-modelled, protected against abuse, careful with personal data, observable, alerting on what users feel, backed up with tested restores, and supported by a runbook and a calm incident process.

## Why this matters to an FDE

AdmitFlow now runs the institute's admissions. If it leaks student data, the institute faces a data-protection complaint. If follow-ups silently stop, students enrol elsewhere. If the database is lost, a year of work is gone. The client may never read your code, but they will remember the day something went wrong, and whether you'd prepared for it.

## Checkpoint

Comfortable with threat models, SLOs, alerting and incident response? Take the [checkpoint](checkpoint.md). Score ≥ 80% **and** complete the [build](build.md) and [break & fix](break-and-fix/README.md) to move on.

## Lessons

| # | Lesson | Core / Stretch | Time |
| --- | --- | --- | --- |
| 01 | [Security foundations: threat modelling and the OWASP Top 10](lessons/01-security-foundations.md) | Core | 4 h |
| 02 | [Protecting data](lessons/02-protecting-data.md) | Core | 3 h |
| 03 | [Protecting against abuse](lessons/03-abuse-protection.md) | Core | 3 h |
| 04 | [Security testing](lessons/04-security-testing.md) | Core | 3 h |
| 05 | [Monitoring and alerting](lessons/05-monitoring-and-alerting.md) | Core | 5 h |
| 06 | [Reliability patterns](lessons/06-reliability-patterns.md) | Core | 3 h |
| 07 | [Incidents: response, communication and learning](lessons/07-incidents.md) | Core | 3 h |
| 08 | [Backups, disaster recovery, audit and compliance](lessons/08-backups-and-compliance.md) | Core | 3 h |

## Practice

[exercises/](exercises/README.md): a threat model, a retention job, and a circuit breaker.

## Build: AdmitFlow, hardened

See [build.md](build.md).

- **Reference solution:** [`security.py`](../../projects/admitflow/admitflow/security.py), [`privacy.py`](../../projects/admitflow/admitflow/privacy.py), [`observability.py`](../../projects/admitflow/admitflow/observability.py), audit log in [`db.py`](../../projects/admitflow/admitflow/db.py), [`deploy/monitoring/alerts.yml`](../../projects/admitflow/deploy/monitoring/alerts.yml), [`docs/runbook.md`](../../projects/admitflow/docs/runbook.md), [`tests/test_production.py`](../../projects/admitflow/tests/test_production.py)

## Break & fix

[break-and-fix/](break-and-fix/README.md): approved follow-ups stopped sending for three days and nobody noticed. Replay it, find six contributing factors, and prove an alert would have caught it in an hour.

## Field Track

See [field-track.md](field-track.md). Run a game day and write the client communication.

## Done when

- [ ] Threat model written; top risks have controls and tests
- [ ] Public and login endpoints rate-limited; security headers on every response; CSP on the dashboard
- [ ] No contact details in logs; AI prompts minimized (tested)
- [ ] Security-relevant actions audited; `GET /audit` admin-only
- [ ] `/metrics` exposed (token-protected); alerts defined with runbook links; outbox alert proven on the incident replay
- [ ] Backup and verified restore done once, recorded in the runbook
- [ ] Incident report and client messages written for the break & fix
- [ ] Game day completed
- [ ] [`progress/self-assessment.md`](../../progress/self-assessment.md) updated

## Resources

See [resources.md](resources.md).

---
*Last verified: 2026-11-21 · Metrics in Prometheus text format; alert rules validated as YAML but not loaded into a running Prometheus in the authoring environment.*
