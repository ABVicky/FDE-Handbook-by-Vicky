# Module 05 — Databases and Data Engineering

> 💡 **In plain words:** Real businesses run on data, and their data is always messy. You'll learn SQL (the language for asking databases questions), how to make slow queries fast, and how to bring data from different systems together reliably.
>
> 🛠️ **What you'll build:** A proper database for AdmitFlow, plus a report that finally answers the director's question: which channels bring students who actually enrol?
>
> ⏭️ **You can skip for now:** Lessons 07–08 are mostly awareness; read them lightly on a first pass.
>
> 🧭 **Comes after:** [Module 04: Software Engineering](../04-software-engineering/README.md) · **Leads to:** [Module 06: Cloud and Infrastructure](../06-cloud-and-infrastructure/README.md)
>
> 🪜 **How to work through it:** read the lessons in order → try the exercises → do the build → do the break & fix → do the Field Track → tick the "Done when" list. New here? Read [Start Here](../../START-HERE.md) first.

**Stage:** 2 — Engineering · **Time:** ~3 weeks at 15–20 h/week · **Builds:** C2 (Build software), C3 (Apply AI and data)
**Prerequisites:** [Module 04](../04-software-engineering/README.md): the AdmitFlow API and dashboard.

## Outcome

After this module you can model data, write analytical SQL, make slow queries fast, move an application onto a real database with migrations, and build a pipeline that turns messy multi-source data into numbers a client can trust.

## Why this matters to an FDE

The pilot worked. Now Ms. Rao asks the question she's wanted answered since Module 01: **"Which channels actually produce students who enrol?"** Answering it means combining AdmitFlow's leads with a different system's admissions records, which have different IDs, name formats and phone formats, and producing a number she'll use to move real advertising budget.

That's FDE data work in miniature: get data out of systems you don't control, match it, store it properly, and report on it in a way you can defend line by line.

## Checkpoint

Comfortable with SQL, indexes and migrations? Take the [checkpoint](checkpoint.md). Score ≥ 80% **and** complete the [build](build.md) and [break & fix](break-and-fix/README.md) to move on.

## Lessons

| # | Lesson | Core / Stretch | Time |
| --- | --- | --- | --- |
| 01 | [Relational thinking and data modelling](lessons/01-data-modelling.md) | Core | 4 h |
| 02 | [SQL fundamentals](lessons/02-sql-fundamentals.md) | Core | 6 h |
| 03 | [Analytical SQL: CTEs and window functions](lessons/03-analytical-sql.md) | Core | 4 h |
| 04 | [Indexes, query plans and transactions](lessons/04-indexes-and-transactions.md) | Core | 4 h |
| 05 | [Python and databases: SQLAlchemy and migrations](lessons/05-sqlalchemy-and-migrations.md) | Core | 5 h |
| 06 | [Data pipelines: ingestion, quality and matching](lessons/06-data-pipelines.md) | Core | 5 h |
| 07 | [NoSQL and caching](lessons/07-nosql-and-caching.md) | Core / Stretch | 2 h |
| 08 | [The modern data stack and data governance](lessons/08-data-stack-and-governance.md) | Core / Stretch | 3 h |

## Practice

[exercises/](exercises/README.md): ten SQL drills on AdmitFlow data (with a self-checking answer script), a data-modelling exercise, and an idempotent loader with history.

## Build: AdmitFlow on a real database, with a pipeline

See [build.md](build.md).

- **Starting point:** your Module 04 API and dashboard
- **Goal:** SQL repository with migrations, an audited ingestion pipeline, admissions matching, and a conversion-by-channel report
- **Reference solution:** [`projects/admitflow/`](../../projects/admitflow/README.md): `admitflow/db.py`, `admitflow/pipeline.py`, `migrations/`

## Break & fix

[break-and-fix/](break-and-fix/README.md): the Monday "neglected leads" report now takes 26 seconds. Make it take milliseconds, and prove why.

## Field Track

See [field-track.md](field-track.md). Write the data-access request you'd send the client's IT team.

## Done when

- [ ] The API runs on SQL (SQLite locally) via `DATABASE_URL`, with schema created by migrations
- [ ] Contract tests pass for both JSON and SQL repositories
- [ ] Ingesting all three files gives **190 leads**; re-running changes nothing
- [ ] Every run is recorded; every rejected row is stored with a reason; counts reconcile
- [ ] Admissions matching links **22** enrolments and reports the **3** unmatched
- [ ] You can explain the conversion-by-channel numbers, including why channel totals exceed 190
- [ ] The break & fix report runs in under 0.1 s, with the query plan to prove it
- [ ] SQL drills done; data inventory written ([Lesson 08](lessons/08-data-stack-and-governance.md))
- [ ] [`progress/self-assessment.md`](../../progress/self-assessment.md) updated

## Resources

See [resources.md](resources.md).

---
*Last verified: 2026-11-21 · Tested with: SQLite 3.54, SQLAlchemy 2.0.58, Alembic (current 1.x), Python 3.9+. PostgreSQL steps are written for PostgreSQL 16 and run in CI; not run on the author's machine.*
