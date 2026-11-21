# Module 05 Build — AdmitFlow on a real database, with a pipeline

**Time:** ~20–25 hours · **Capabilities:** C2, C3

## Scenario

Two things happened after the pilot:

1. Mr. Okafor (IT) says: *"A JSON file isn't acceptable for production. We need a proper database with backups."*
2. Ms. Rao asks: *"Which channels produce students who actually **enrol**?"* The admissions office has sent an export from the student information system (SIS): [`admissions_export.csv`](../../projects/admitflow/data/admissions_export.csv). It uses its own student numbers, writes names as `"SURNAME, Given"`, and sometimes stores phones with a leading `0`.

## Requirements

### 1. SQL storage
- `SqlRepository` implementing the same `Repository` interface (SQLAlchemy 2.0), selected by `DATABASE_URL`
- Normalized schema: `leads`, `lead_sources` (one row per channel), `notes`, `followups`, `users`, plus `import_runs` and `rejected_rows`
- Constraints and indexes justified by real queries
- Schema created and changed **only by Alembic migrations**; a test that runs `upgrade → check → downgrade → upgrade`
- **Contract tests** running identical tests against JSON and SQL repositories; API tests running against both

### 2. Ingestion pipeline
```bash
admitflow ingest --website data/leads_sample.csv --ads data/ad_leads.csv --walkins data/walkins.csv
```
- **Idempotent:** a file already loaded is skipped (checksum); `--force` re-processes it without creating duplicates
- **Auditable:** each run is recorded with counts and status
- **Reconcilable:** read = new + merged + rejected, checked on every run
- Rejected rows stored with line number and reason

### 3. Admissions matching
```bash
admitflow match-admissions data/admissions_export.csv
```
- Match on email, else phone **and** name (normalizing the SIS formats)
- Mark matched leads `enrolled`, recording the student number and enrolment date
- Idempotent: re-running matches nothing new
- Report unmatched admissions with a reason

### 4. Report
```bash
admitflow report
```
Leads, enrolments and conversion rate by channel, with the definition written down.

## Expected results

```
leads_sample.csv: read 120, new 120, merged 0, rejected 0
ad_leads.csv: read 60, new 50, merged 10, rejected 0
walkins.csv: read 25, new 20, merged 5, rejected 0
matched 22, already matched 0, unmatched 3
```

```
channel     leads  enrolled  conversion
ad             92        11       12.0%
website        52         7       13.5%
walk-in        36         4       11.1%
phone          12         3       25.0%
whatsapp       11         0        0.0%
```

## The conversation this report starts

Before sending these numbers to Ms. Rao, write a short **interpretation note** (`my-work/m05/report-note.md`) covering:
- **Definition:** a lead counts once *per channel it used* (203 channel-leads from 190 people), so per-channel figures overlap.
- **Small numbers:** phone's 25% is 3 students out of 12. Don't move budget on that alone.
- **Data gaps:** 3 admissions matched no lead. Were they direct applications, or enquiries that were never recorded?
- **Time window:** one month of enquiries; many September leads may still enrol later.
- **What you'd need** to answer "which **ad campaigns** work": campaign IDs are in `ad_leads.csv` (`campaign_name`), but you're not storing them as a column yet. That's a good next step.

This note matters as much as the code. A correct number presented without its caveats can drive a bad decision.

## Running the reference solution

```bash
cd projects/admitflow
```

```bash
python -m pip install -e ".[api,db,dev]"
```

```bash
export DATABASE_URL=sqlite:///admitflow.db
```

```bash
alembic upgrade head
```

```bash
admitflow ingest --website data/leads_sample.csv --ads data/ad_leads.csv --walkins data/walkins.csv
```

```bash
admitflow match-admissions data/admissions_export.csv
```

```bash
admitflow report
```

`admitflow serve` now serves the dashboard from the database.

## Done when

- [ ] Expected results above reproduced
- [ ] Re-running ingest and matching changes nothing
- [ ] Contract tests and API tests pass against both repositories
- [ ] Migration test passes; `alembic check` reports no drift
- [ ] Interpretation note written
- [ ] ≥ 80% coverage

## Stretch

- Store `campaign_name` and report conversion **by campaign**
- A file-level check that fails the whole run (before loading) if expected columns are missing
- Fuzzy matching for unmatched admissions, producing a **review list** for a human rather than auto-linking
- Run against PostgreSQL in Docker (Module 06) and compare `EXPLAIN ANALYZE` output
