# Integration patterns cookbook

Short recipes, each pointing to tested code in AdmitFlow.

| Recipe | Use when | Code | Lesson |
| --- | --- | --- | --- |
| **Verify a signed webhook** | Receiving events from another system | [`integrations/webhooks.py`](../../projects/admitflow/admitflow/integrations/webhooks.py) | [M09 L03](../../modules/09-enterprise-integration/lessons/03-webhooks.md) |
| **Idempotent webhook processing** | Senders retry; events arrive twice | `website_form_webhook` in [`api/routes.py`](../../projects/admitflow/admitflow/api/routes.py) + `record_event` | M09 L03 |
| **Search-before-create sync** | Pushing records into a CRM/ERP without duplicates | [`integrations/crm.py`](../../projects/admitflow/admitflow/integrations/crm.py) | [M09 L04](../../modules/09-enterprise-integration/lessons/04-calling-third-party-apis.md) |
| **Outbox for side effects** | Sending messages after a database change, reliably | [`integrations/messaging.py`](../../projects/admitflow/admitflow/integrations/messaging.py) | M09 L02 |
| **Retry with backoff** | Transient network errors, 429, 5xx | `CrmClient._request`; [interview solution 8](../../interview-prep/solutions/coding_solutions.py) | M03 L14 |
| **Audited file ingestion** | Regular CSV exports from systems you don't control | [`pipeline.py`](../../projects/admitflow/admitflow/pipeline.py) | [M05 L06](../../modules/05-databases-and-data-engineering/lessons/06-data-pipelines.md) |
| **Cross-system matching** | Linking records with different IDs (SIS ↔ leads) | `match_admissions` in `pipeline.py` | M05 L06 |
| **Verify an OIDC ID token** | Staff sign-in with Google/Entra/Okta | [`integrations/oidc.py`](../../projects/admitflow/admitflow/integrations/oidc.py) | [M09 L05](../../modules/09-enterprise-integration/lessons/05-identity-and-sso.md) |
| **Test against a fake service** | Any third-party API | `FakeCrm` in [`tests/test_integrations.py`](../../projects/admitflow/tests/test_integrations.py); `httpx.MockTransport` | M09 L04 |

## The questions to ask about every integration
1. What happens if this runs twice?
2. What happens if it times out halfway?
3. Who owns each end, and who gets told when it breaks?
4. How would we know it stopped working?
