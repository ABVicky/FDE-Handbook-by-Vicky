# Lesson 04 — Security testing

**Time:** ~3 hours · **Core**

## Layers of security testing

| Layer | What | AdmitFlow |
| --- | --- | --- |
| **Security unit/integration tests** | Every access rule and attack you've thought of, as a test | 401/403 tests per route; webhook signature/replay; MCP scope; rate limits; redaction |
| **Dependency scanning** | Known vulnerabilities in libraries and images | `pip-audit`, `npm audit`, image scanning (Trivy / registry scanner) in CI |
| **Static analysis** | Risky code patterns | `bandit` (Python), linters with security rules |
| **Secret scanning** | Committed credentials | GitHub secret scanning / push protection; `gitleaks` |
| **Red teaming AI features** | Adversarial prompts | Injection cases in the evaluation set (Module 08) |
| **Penetration test** | Experts attack the running system | Before handling large volumes of sensitive data, or when the client requires it |

## Write the attack as a test

When you think of an attack, write it down as a test so it can never silently come back:

```python
def test_counsellor_cannot_change_someone_elses_lead(client): ...
def test_redelivered_event_is_idempotent(api, repo): ...
def test_get_lead_hides_other_counsellors_leads(setup): ...
def test_login_is_rate_limited_and_audited(api): ...
def test_drafter_sends_minimal_personal_data(): ...
```

AdmitFlow has several dozen such tests across `test_api.py`, `test_integrations.py`, `test_mcp.py` and `test_production.py`. A security reviewer reading them learns more than from any document.

## Dependencies

Most of your code is other people's code. In CI:

```bash
python -m pip install pip-audit
```

```bash
pip-audit
```

```bash
cd web && npm audit --audit-level=high
```

Then decide: upgrade, accept with a written reason (not exploitable in our use), or replace. Keep dependencies few (Module 03, Lesson 09) and pinned, and update on a schedule rather than in a panic.

## Secrets in Git

Turn on secret scanning and push protection on the repository. If a secret is ever committed: **rotate it first**, then remove it, then check access logs at the provider.

## Pen tests and bug reports

A penetration test is valuable once the system holds real data at scale. Prepare: scope (URLs, roles, test accounts **in a staging environment** with synthetic data), rules of engagement, dates, contacts. Fix findings by severity and retest.

Publish a way to report vulnerabilities (a `SECURITY.md` with a contact). It's cheap, and some clients' security questionnaires ask for it.

## Check yourself

Add `pip-audit` and `npm audit` steps to AdmitFlow's CI workflow, failing on high-severity findings. Run them locally first. For every finding, write one line: upgrade / accept (why) / replace.

Next: [Lesson 05 — Monitoring and alerting](05-monitoring-and-alerting.md)
