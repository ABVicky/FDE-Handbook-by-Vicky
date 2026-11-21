# Module 06 Build — AdmitFlow, deployed

**Time:** ~25–30 hours · **Capabilities:** C4

## Scenario

The pilot went well. Mr. Fernandes wants AdmitFlow running for the whole admissions team from next month. Ms. Chen will approve it once she has a monthly cost estimate. Mr. Okafor has two conditions: *"I need to be able to restart it, see its logs and restore a backup, without calling you. And no passwords in emails."*

## Requirements

### 1. Containers
- API image: multi-stage, non-root, health check, no secrets, configuration from environment
- Dashboard image: static build served by a small web server, with security headers
- `.dockerignore` files

### 2. Local environment
- `docker compose up --build` starts database, migrations, API and dashboard in the right order
- Database data on a named volume
- Required secrets enforced (Compose refuses to start without them)
- A README section: first-time setup, loading data, creating a user

### 3. CI/CD
- On every pull request: backend tests (two Python versions, **real PostgreSQL**), frontend type-check/build/test, image build and smoke test
- Branch protection on `main` requiring the checks
- *Stretch:* on merge, push images tagged with the commit SHA and deploy to staging

### 4. Cloud deployment
On **one** provider of your choice (free tier or trial):
- Managed PostgreSQL with backups and no public IP (or the closest your tier allows; document the gap)
- API on a managed container platform over HTTPS; startup/readiness on `/ready`, liveness on `/health`
- Secrets in the secret manager; a dedicated least-privilege service identity
- Migrations run as a separate step before the new version takes traffic
- Dashboard deployed and logging in successfully
- Scheduled weekly ingest (or documented exactly for your platform)
- **A rollback performed and recorded**

> No cloud account? Deploy with Compose to a local VM or spare machine, and write the cloud plan in the deployment guide instead. Say so clearly in your write-up.

### 5. Documents
- Deployment guide ([template](../../templates/deployment-guide.md)), including the configuration table and go-live checklist
- Cost estimate ([Exercise 03](exercises/03-cost-estimate.md))
- An ADR for your platform choice

## Done when

- [ ] A fresh clone + `.env` + `docker compose up --build` works on another person's machine
- [ ] CI is green and required; a deliberately failing PR is blocked
- [ ] The deployed system is reachable over HTTPS and a counsellor account can log in
- [ ] `/ready` turns `503` when you stop the database (try it), and the platform stops routing traffic
- [ ] You rolled back to the previous version and back again
- [ ] Mr. Okafor's three needs (restart, logs, restore) are each covered by a numbered procedure in the deployment guide
- [ ] **Everything you created for practice is deleted afterwards**, and the bill confirmed

## Reference solution

- [`projects/admitflow/Dockerfile`](../../projects/admitflow/Dockerfile), [`web/Dockerfile`](../../projects/admitflow/web/Dockerfile), [`web/nginx.conf`](../../projects/admitflow/web/nginx.conf)
- [`projects/admitflow/docker-compose.yml`](../../projects/admitflow/docker-compose.yml) and [`.env.example`](../../projects/admitflow/.env.example)
- [`.github/workflows/admitflow-ci.yml`](../../.github/workflows/admitflow-ci.yml)
- [`projects/admitflow/deploy/README.md`](../../projects/admitflow/deploy/README.md) (Cloud Run walkthrough + AWS/Azure equivalents) and [`deploy/terraform-cloud-run/main.tf`](../../projects/admitflow/deploy/terraform-cloud-run/main.tf)
- New in the API for this module: `/ready`, and `admitflow serve` reading `HOST`/`PORT` from the environment
