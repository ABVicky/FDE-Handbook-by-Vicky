# Module 06 — Checkpoint

Pass mark: **10 / 12**, plus the [build](build.md) and [break & fix](break-and-fix/README.md).

---

**1.** Explain the difference between IaaS, PaaS and a managed service, with an AdmitFlow example of each.

**2.** What is the shared responsibility model? Give two things that are always *your* responsibility in the cloud.

**3.** What's the difference between a Docker image and a container?

**4.** Why does the AdmitFlow Dockerfile copy `pyproject.toml` and install dependencies *before* copying the rest of the code?

**5.** A containerized API logs `Uvicorn running on http://127.0.0.1:8000`, and `curl localhost:8000` from the host fails. Why?

**6.** In Docker Compose, the API's `DATABASE_URL` uses `localhost:5432` and can't connect. What should it be, and why?

**7.** What does `depends_on` without a `condition` guarantee, and what doesn't it?

**8.** Name three things AdmitFlow's CI checks that a plain "run pytest" workflow wouldn't.

**9.** What's the difference between a liveness check and a readiness check? Which one should touch the database?

**10.** Where should `ADMITFLOW_SECRET_KEY` live in (a) local development, (b) CI, (c) production? Where must it never be?

**11.** You need to rename the column `course` to `programme` without downtime. Outline the steps.

**12.** Name three ways to keep a cloud bill predictable.

---

<details>
<summary><strong>Answers</strong></summary>

1. IaaS: you manage the OS (the office VM). PaaS: you bring the app, the platform runs it (Cloud Run / App Runner for the API). Managed service: the provider runs the whole component (Cloud SQL / RDS for PostgreSQL).
2. The provider secures the underlying infrastructure; you secure what you configure and put in it. Always yours: identities and permissions (IAM), your data, secrets, network exposure (firewall rules, public buckets), application code.
3. An image is a read-only template built from a Dockerfile; a container is a running (or stopped) instance of it.
4. Layer caching: dependency installation is slow and changes rarely, so putting it first means code-only changes rebuild in seconds.
5. Inside the container, `127.0.0.1` is the container's own loopback. Traffic forwarded from the host arrives on the container's network interface, where nothing listens. Bind to `0.0.0.0`.
6. `db:5432` (the Compose service name). Inside the api container, `localhost` is the api container itself.
7. It guarantees start **order** only. It doesn't wait for the dependency to be **ready** (e.g. PostgreSQL accepting connections) or for a migration to finish. Use `condition: service_healthy` / `service_completed_successfully`.
8. Any three: tests on two Python versions; tests against real PostgreSQL; tests in two time zones; migrations applied and `alembic check` for drift; frontend strict type-check and build; Docker images built and smoke-tested.
9. Liveness: "is the process alive?" (restart if not), cheap, no dependencies. Readiness: "can it serve now?" (route traffic only if yes); this one checks the database.
10. (a) A `.env` file that's git-ignored; (b) GitHub Actions secrets (or no long-lived secret at all, via OIDC); (c) the cloud secret manager, injected at runtime. Never in Git, images, logs, tickets or chat.
11. Expand and contract: add `programme` (nullable) → deploy code that writes both and reads `programme` with fallback → backfill → deploy code that uses only `programme` → later, drop `course`. Back up before each migration.
12. Budget alerts to you and the client; caps (`max_instances`, log retention); labels on every resource; right-size the database; delete unused resources; monthly bill review.

</details>
