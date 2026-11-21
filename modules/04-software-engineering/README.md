# Module 04 — Software Engineering

> **In plain words:** Now your program becomes a real web application: a website counsellors log into, backed by a server that keeps their data safe. You'll learn how the pieces talk to each other and how professionals keep code tidy and tested.
>
> **What you'll build:** AdmitFlow's first real version: a login, a list of enquiries, notes and follow-ups, in a web dashboard.
>
> **You can skip for now:** Stretch topics (GraphQL, Next.js, design patterns). The React lessons can feel like a lot; aim to understand, not to memorize.
>
> **Comes after:** [Module 03: Programming Fundamentals](../03-programming-fundamentals/README.md) · **Leads to:** [Module 05: Databases and Data Engineering](../05-databases-and-data-engineering/README.md)
>
> **How to work through it:** read the lessons in order → try the exercises → do the build → do the break & fix → do the Field Track → tick the "Done when" list. New here? Read [Start Here](../../START-HERE.md) first.

**Stage:** 2 — Engineering · **Time:** ~5 weeks at 15–20 h/week · **Builds:** C2 (Build software)
**Prerequisites:** [Module 03](../03-programming-fundamentals/README.md): Python with tests, basic JavaScript/TypeScript, Git with pull requests.

## Outcome

After this module you can build a full-stack web application: a clean, documented HTTP API with authentication and authorization, a React + TypeScript frontend, and a test suite you trust. You can also work productively in a codebase you didn't write.

## Why this matters to an FDE

The AdmitFlow CLI works, but counsellors don't use terminals. They need a dashboard on their laptops, one login each, and a guarantee that one counsellor can't overwrite another's leads. The director wants numbers without asking you.

Almost every FDE engagement ends up here: a small, reliable web application wrapped around the client's data. Clients judge you on whether it works on Monday morning, whether it's secure, and whether their team can maintain it after you leave. That depends on engineering practice (API design, validation, auth, tests, documentation) far more than on clever code.

## Checkpoint

Built web APIs and React apps before? Take the [checkpoint](checkpoint.md). Score ≥ 80% **and** complete the [build](build.md) and [break & fix](break-and-fix/README.md) to move on.

## Lessons

| Week | # | Lesson | Core / Stretch | Time |
| --- | --- | --- | --- | --- |
| 1 | 01 | [How a web application fits together](lessons/01-web-app-architecture.md) | Core | 2 h |
| 1 | 02 | [Designing HTTP APIs](lessons/02-api-design.md) | Core | 4 h |
| 1 | 03 | [FastAPI fundamentals](lessons/03-fastapi.md) | Core | 6 h |
| 2 | 04 | [Authentication and authorization](lessons/04-auth.md) | Core | 5 h |
| 2 | 05 | [Errors, logging, middleware and background work](lessons/05-errors-logging-middleware.md) | Core | 3 h |
| 3 | 06 | [Frontend fundamentals: HTML, CSS and React](lessons/06-react.md) | Core | 8 h |
| 3 | 07 | [Connecting frontend and backend](lessons/07-frontend-backend.md) | Core | 4 h |
| 4 | 08 | [Testing strategy](lessons/08-testing-strategy.md) | Core | 4 h |
| 4 | 09 | [Engineering practice: structure, reviews, docs, unfamiliar code](lessons/09-engineering-practice.md) | Core | 4 h |

**Stretch topics** (flagged in lessons): Node.js/Express, GraphQL, Next.js, design patterns and SOLID, Django.

## Practice

[exercises/](exercises/README.md): API design on paper, a FastAPI mini-service with auth and tests, a React component, and a code review.

## Build: AdmitFlow v1, the counsellor dashboard

See [build.md](build.md). It runs through weeks 2–5.

- **Starting point:** your Module 03 CLI
- **Goal:** FastAPI backend (leads, notes, follow-ups, login, roles) + React counsellor dashboard
- **Reference solution:** [`projects/admitflow/`](../../projects/admitflow/README.md) (`admitflow/api/`, `web/`)

## Break & fix

[break-and-fix/](break-and-fix/README.md): you inherit an undocumented follow-up service with a failing test suite. Make the tests pass, find the security hole, and write the missing README.

## Field Track

See [field-track.md](field-track.md). Scope and estimate the dashboard before building it, then compare your estimate with reality.

## Done when

- [ ] A counsellor can log in, see and filter leads, open one, add notes, change its status and schedule follow-ups
- [ ] Only admins can assign leads; counsellors can't change leads assigned to someone else
- [ ] Invalid input returns `422` with field-level messages; missing auth returns `401`; forbidden actions return `403`
- [ ] The API has integration tests (≥ 80% coverage) and generated docs at `/docs`
- [ ] The frontend type-checks with `strict` TypeScript and has at least one test
- [ ] You wrote at least two ADRs
- [ ] The break & fix service passes its tests and has a README
- [ ] Your estimate is compared with actual time spent
- [ ] [`progress/self-assessment.md`](../../progress/self-assessment.md) updated

## Resources

See [resources.md](resources.md).

---
*Last verified: 2026-11-21 · Tested with: Python 3.9+, FastAPI 0.128, Pydantic 2.13, PyJWT 2.15, React 18.3, Vite 5.4, TypeScript 5.6, Vitest 2.1*
