# Lesson 07 — Configuration, secrets, environments and releases

**Time:** ~3 hours · **Core**

## Why this matters

All four break & fix problems in this module were **configuration**, not code. Most production incidents at FDE clients are too: a wrong URL, a missing secret, a setting copied from a laptop. This lesson is about making configuration explicit, safe and checkable.

## Twelve-factor configuration

Keep configuration **in the environment**, separate from code, so the same image runs everywhere:

| Setting | Local | Staging | Production |
| --- | --- | --- | --- |
| `DATABASE_URL` | `sqlite:///admitflow.db` | staging Cloud SQL | production Cloud SQL |
| `ADMITFLOW_SECRET_KEY` | random, in `.env` | secret manager | secret manager (different value!) |
| `ADMITFLOW_CORS_ORIGINS` | `http://localhost:5173` | `https://staging.admitflow…` | `https://admitflow.northbridge.example` |
| `TZ` | your zone | `Asia/Kolkata` | `Asia/Kolkata` |

Document every variable in one place (`.env.example`, plus the deployment guide's configuration table).

## Fail fast on bad configuration

The app should refuse to start, or fail clearly, when required configuration is missing or invalid, instead of failing later with a confusing error:

```python
def secret_key() -> str:
    key = os.environ.get("ADMITFLOW_SECRET_KEY")
    if not key or len(key) < 32:
        raise RuntimeError("ADMITFLOW_SECRET_KEY must be set to a random value of at least 32 characters…")
    return key
```

Compose's `${VAR:?message}` and a readiness check (`/ready`) are the same idea at other layers.

*Stretch:* `pydantic-settings` validates all configuration at startup into one typed object.

## Secrets

| Do | Don't |
| --- | --- |
| Use the platform's secret manager | Commit secrets to Git (even private repos), or bake them into images |
| Give each environment different secrets | Reuse the production key in staging |
| Grant read access only to the service account that needs it | Share one admin key across systems |
| Rotate on a schedule and **immediately** if exposed | Paste secrets into chat, tickets or logs |
| Prefer short-lived credentials (OIDC, managed identities) | Create long-lived access keys for CI |

If a secret leaks: **revoke and rotate first**, then clean up. Removing it from Git history doesn't un-leak it.

## Environments

At minimum: **local → staging → production**. Staging should resemble production (same images, same database engine, realistic but **non-real** data). Never use real student data outside production unless the client explicitly approves it and it's anonymized.

## Releases: rollouts and rollbacks

- **Immutable, versioned images:** tag with the commit SHA. "Which version is running?" always has an exact answer.
- **Rollback = redeploy the previous image** (Cloud Run: shift traffic to the previous revision). Practise it once *before* you need it.
- **Gradual rollout** (*stretch*): send 10% of traffic to the new revision, watch errors, then 100%.

## Database changes during releases

Code can be rolled back in seconds. Data can't. So migrations must be **backward compatible** with the version still running ("expand and contract"):

1. **Expand:** add new things (nullable columns, new tables). Old code ignores them.
2. **Deploy** code that writes both old and new.
3. **Backfill** existing data.
4. **Contract:** remove the old column in a *later* release, once nothing uses it.

Never rename or drop a column in the same release as the code change that stops using it. And always confirm a recent backup exists before running a migration in production.

## Check yourself

Write the configuration table for AdmitFlow production: every variable and secret, where it lives, who can read it, and how to rotate it. Add it to your deployment guide ([template](../../../templates/deployment-guide.md)).

Next: [Lesson 08 — Infrastructure as Code, Kubernetes and cost](08-iac-kubernetes-cost.md)
