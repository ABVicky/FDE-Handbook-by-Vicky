# Capstone briefs

Choose **one**, in a domain different from AdmitFlow. You work independently: the briefs describe a client and a problem, not a solution. Everything else (discovery, scope, data, architecture, evaluation, deployment, handover) is yours.

| Brief | Client (fictional) | Core challenge |
| --- | --- | --- |
| [A. Enterprise knowledge assistant](a-knowledge-assistant.md) | Harbor Freight Logistics: 400 staff, policies across many documents | RAG with **document-level permissions** and SSO |
| [B. Intelligent workflow automation](b-workflow-automation.md) | Meridian Supplies: 1,200 supplier invoices a month typed by hand | Document extraction, validation, **human review**, ERP integration |
| [C. Operations analytics copilot](c-analytics-copilot.md) | Greenleaf Community Clinics: managers can't get answers from their data | Data pipeline + **safe text-to-SQL** with guardrails and evaluation |
| [D. Bring your own client](d-bring-your-own.md) | A real organization you find | Whatever their problem actually needs |

## Every capstone must include

1. Problem statement and discovery notes (real or role-played interviews; observation if possible)
2. Current-state workflow map
3. Requirements with acceptance criteria and an explicit out-of-scope list
4. Architecture diagram and ADRs for key choices
5. Data model and API documentation
6. Working, **deployed** code with tests and CI
7. Evaluation report for any AI component, with real numbers against a baseline
8. Security and privacy review
9. Deployment guide, runbook and monitoring (with at least one meaningful alert)
10. Business impact: before vs after, or a credible estimate with labelled assumptions
11. A 10-minute recorded client presentation and a handover document

**Real users rule:** at least one person other than you must use it for a real (or realistically simulated) task, and you must report what happened.

## Grading rubric (self or peer)

| Criterion | 1: Not yet | 2: Solid | 3: Field-ready |
| --- | --- | --- | --- |
| Problem understanding | Solution-first | Clear problem and metrics | Root causes found; stakeholders' goals reconciled |
| Engineering quality | Works on my machine | Tested, deployed, documented | CI, migrations, observability, clean handover |
| AI quality (if used) | Demo only | Evaluated against a baseline | Evaluation in CI; failure modes designed for |
| Security & privacy | Not considered | Review written, main risks controlled | Threat model with tests; data minimized |
| Business impact | Asserted | Estimated with assumptions | Measured with real users, honestly reported |
| Communication | Technical jargon | Clear presentation | Client could decide from it; limitations explicit |
| Ownership & handover | None | Docs exist | Someone else ran it from your docs |
