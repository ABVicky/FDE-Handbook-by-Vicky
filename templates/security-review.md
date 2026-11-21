# Security & Privacy Review — <System>

**Prepared by:** · **For:** (client security / IT / privacy team) · **Date:** · **Version:**

Answer plainly. Reviewers trust a clear "we don't do X yet; here's the plan" more than vague assurances.

## 1. System overview
<One paragraph and an architecture diagram showing every component, network boundary and external service.>

## 2. Data inventory
| Data | Classification (public / internal / personal / sensitive) | Where stored | Retention | Who can access |
| --- | --- | --- | --- | --- |

## 3. Data flows
| From → To | Data | Transport / encryption | Authentication |
| --- | --- | --- | --- |
| Browser → API | | HTTPS (TLS 1.2+) | User session token |
| API → database | | | |
| API → third parties (LLM provider, CRM, messaging) | | | |

For each third party: what data, which region, their retention and training-use terms, contract in place?

## 4. Identity and access
- How users sign in (SSO? MFA enforced by whom?)
- Roles and what each can do
- How leavers lose access
- Service accounts / API keys: what they can do, where stored, rotation

## 5. Application security
- Input validation, output encoding, CSRF/CORS settings
- Secrets management
- Dependency and image scanning
- Logging: what's logged, and confirmation that secrets and unnecessary personal data are not
- AI-specific: prompt injection measures, tool permissions, human approval points, evaluation results

## 6. Infrastructure
- Hosting, regions, network exposure (public endpoints, private database)
- Backups, encryption at rest, tested restore date
- Monitoring and alerting

## 7. Incident response
Who is contacted, how fast, and how affected individuals would be notified.

## 8. Known gaps and plan
| Gap | Risk | Mitigation now | Fix by |
| --- | --- | --- | --- |

*Worked example: [AdmitFlow Module 09 build](../modules/09-enterprise-integration/build.md#security-review)*
