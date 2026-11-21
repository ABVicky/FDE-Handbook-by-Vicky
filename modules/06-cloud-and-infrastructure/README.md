# Module 06 — Cloud and Infrastructure

> **In plain words:** An app on your laptop helps nobody. Here you'll learn to package your app so it runs anywhere, test every change automatically, and put it online in the cloud.
>
> **What you'll build:** AdmitFlow running online, with automatic tests on every change and a written guide for keeping it running.
>
> **You can skip for now:** Kubernetes and Terraform (stretch). You can do the build without a cloud account by running everything on your own machine.
>
> **Comes after:** [Module 05: Databases and Data Engineering](../05-databases-and-data-engineering/README.md) · **Leads to:** [Module 07: AI and Machine Learning Fundamentals](../07-ai-and-machine-learning/README.md)
>
> **How to work through it:** read the lessons in order → try the exercises → do the build → do the break & fix → do the Field Track → tick the "Done when" list. New here? Read [Start Here](../../START-HERE.md) first.

**Stage:** 2 — Engineering · **Time:** ~4 weeks at 15–20 h/week · **Builds:** C4 (Deploy and integrate)
**Prerequisites:** [Module 05](../05-databases-and-data-engineering/README.md): AdmitFlow on SQL with migrations. A free GitHub account; a cloud free tier or trial for the deployment lessons (optional, but strongly recommended).

## Outcome

After this module you can containerize an application, run a multi-service system locally with one command, test and build every change automatically, deploy to a managed cloud platform with secrets handled properly, roll back, and explain the monthly cost.

## Why this matters to an FDE

A system that only runs on your laptop delivers no value. AdmitFlow now has to run every day on infrastructure the institute can afford and that Mr. Okafor (part-time IT) can keep alive. FDEs deploy into environments they don't fully control: the client's cloud account, a restricted VM, a security review. Containers, CI and explicit configuration are what make that repeatable instead of heroic.

## Checkpoint

Already shipping containers through CI to the cloud? Take the [checkpoint](checkpoint.md). Score ≥ 80% **and** complete the [build](build.md) and [break & fix](break-and-fix/README.md) to move on.

## Lessons

| # | Lesson | Core / Stretch | Time |
| --- | --- | --- | --- |
| 01 | [Cloud fundamentals](lessons/01-cloud-fundamentals.md) | Core | 3 h |
| 02 | [Linux servers and SSH](lessons/02-linux-and-ssh.md) | Core | 4 h |
| 03 | [Docker](lessons/03-docker.md) | Core | 6 h |
| 04 | [Docker Compose](lessons/04-docker-compose.md) | Core | 3 h |
| 05 | [CI/CD with GitHub Actions](lessons/05-ci-cd.md) | Core | 4 h |
| 06 | [Deploying to the cloud](lessons/06-deploying.md) | Core | 6 h |
| 07 | [Configuration, secrets, environments and releases](lessons/07-config-secrets-releases.md) | Core | 3 h |
| 08 | [Infrastructure as Code, Kubernetes and cost](lessons/08-iac-kubernetes-cost.md) | Core / Stretch | 4 h |

## Practice

[exercises/](exercises/README.md): containerize a service, write its CI workflow, estimate AdmitFlow's monthly cost, and Linux server drills.

## Build: AdmitFlow, deployed

See [build.md](build.md).

- **Starting point:** your Module 05 AdmitFlow
- **Goal:** images, Compose, CI with PostgreSQL, a cloud deployment with secrets, a scheduled ingest, a tested rollback, a deployment guide and a cost estimate
- **Reference solution:** [`Dockerfile`](../../projects/admitflow/Dockerfile), [`docker-compose.yml`](../../projects/admitflow/docker-compose.yml), [`deploy/`](../../projects/admitflow/deploy/README.md), [`.github/workflows/admitflow-ci.yml`](../../.github/workflows/admitflow-ci.yml)

## Break & fix

[break-and-fix/](break-and-fix/README.md): the previous engineer's deployment "works on my laptop" but no counsellor can log in. Diagnose four configuration problems from logs alone.

## Field Track

See [field-track.md](field-track.md). Plan a deployment into a client environment with restrictions and a security review.

## Done when

- [ ] `docker compose up --build` starts database, migrations, API and dashboard; you can log in at http://localhost:8080
- [ ] Images run as non-root, contain no secrets, and pass a health check
- [ ] CI runs tests (including PostgreSQL), builds images and smoke-tests them on every pull request, and branch protection requires it
- [ ] AdmitFlow (or the course service) deployed to a cloud platform over HTTPS, with secrets in a secret manager
- [ ] Rollback performed once, on purpose
- [ ] Scheduled ingest configured (or documented for the target platform)
- [ ] Deployment guide and cost estimate written
- [ ] Break & fix diagnosis written up
- [ ] [`progress/self-assessment.md`](../../progress/self-assessment.md) updated

## Resources

See [resources.md](resources.md).

---
*Last verified: 2026-11-21 · Docker, Compose, cloud and Terraform steps were written against current documentation but **not executed** in the authoring environment; YAML files were validated and CI builds the images. Please open an issue if a step fails for you.*
