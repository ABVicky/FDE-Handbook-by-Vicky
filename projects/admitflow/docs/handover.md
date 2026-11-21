# AdmitFlow — Handover

**From:** FDE · **To:** Northbridge Institute (Mr. Fernandes, Mr. Okafor, Ms. Chen) · **Status:** draft for sign-off (Module 11)

## 1. What exists
AdmitFlow brings every enquiry (website, ads, phone, walk-ins, WhatsApp) into one list, helps counsellors follow up quickly, answers students' course questions from the institute's own documents, drafts follow-up messages for approval, and reports enrolments by channel. Architecture: [ROADMAP §5](../../../ROADMAP.md#5-the-running-project-admitflow); deployment: [deploy/README.md](../deploy/README.md).

## 2. Who owns what
| Area | Owner | Backup | Documents |
| --- | --- | --- | --- |
| Daily use; training new staff | Mr. Fernandes | Priya (champion) | [User guide](user-guide.md) |
| Accounts and access | Mr. Okafor | Mr. Fernandes | [Runbook: offboarding](runbook.md#offboard-a-staff-member) |
| Operations: alerts, backups, restarts | Mr. Okafor | Support contract | [Runbook](runbook.md) |
| Course documents for the assistant | Admissions office | Mr. Fernandes | `data/course_docs/`; run `admitflow eval-assistant` after any change |
| Costs and vendor contracts | Ms. Chen | — | Module 06 cost estimate; monthly bill review |
| Code changes | Future developer / vendor | — | README, [ADRs](adr/), tests, CI |

## 3. Access to transfer
Cloud account and billing; database; secret manager entries (session key, webhook secret, CRM, SMTP, WhatsApp, LLM key, metrics token); Google sign-in client; GitHub repository. Each moves to an institute-owned account, and the FDE's access is removed, with dates recorded here.

## 4. Known issues and limitations
| Issue | Impact | Workaround | Plan |
| --- | --- | --- | --- |
| Messaging is at-least-once | Rare duplicate message after a crash | None needed | Accepted (ADR-006) |
| Offline assistant misses some paraphrases | ~10% of test questions not fully answered | Counsellor contact shown | Evaluate the Claude engine (evaluation report) |
| Lead scoring adds little | — | Priority list orders by waiting time first | Re-evaluate after the next intake (ADR-004) |
| Dashboard screens for drafts, adding enquiries, Google sign-in and the team view | Users rely on the API or an admin for these tasks | Admin performs them via the API docs at `/docs` | Recovery plan, weeks 1–2 |
| No automatic user provisioning (SCIM) | Leavers removed manually | Weekly review by Mr. Okafor | Phase 2 |

## 5. Outcomes so far
| Metric | Baseline | Target | Latest |
| --- | --- | --- | --- |
| Enquiries contacted within 24 h | ~45% (estimate) | ≥ 85% | *to be filled from the dashboard* |
| Duplicate counsellor contacts | unknown | < 2% | |
| Enrolment by channel visible weekly | no | yes | yes |

## 6. Recommended next steps
1. Team view polish and retire the last spreadsheet (high value, small effort)
2. Campaign-level conversion reporting for the ad budget (high value, medium)
3. Evaluate the Claude assistant engine on the evaluation set; switch if it beats the offline engine (medium value, small)
4. SCIM provisioning (medium value, medium)
