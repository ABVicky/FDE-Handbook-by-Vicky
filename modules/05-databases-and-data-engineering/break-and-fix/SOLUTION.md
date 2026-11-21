# Break & Fix — Solution

> ⚠️ Try it properly first.

Fixed script: [`solution/fast_report.py`](solution/fast_report.py)

## Diagnosis

```
SCAN l
CORRELATED SCALAR SUBQUERY 1
SCAN n
```

For each of the ~13,000 open leads, the `NOT EXISTS` subquery **scans all ~80,000 notes**, about a billion row checks. With no index on `notes.lead_id`, the database has no way to find one lead's notes except reading them all. The data grew roughly linearly, but the work grew with *leads × notes*, which is why it went from "under a second" to "half a minute" without anyone changing the code.

Wrapping the column in `date(n.created_at)` makes it worse: even with an index on `created_at`, the function would have to be computed for every row.

## Fix

```sql
CREATE INDEX ix_notes_lead_created ON notes (lead_id, created_at);
```

and compare the raw column with a precomputed boundary:

```sql
AND n.created_at >= ?        -- parameter: '2026-11-06' (as-of date minus 14 days)
```

ISO-format text (`2026-11-06 14:03:00`) sorts in date order, so string comparison is correct. Two equivalent conditions give identical results.

## Proof

| | Time | Plan for `notes` |
| --- | --- | --- |
| Before | **26.54 s** | `SCAN n` |
| After | **0.007 s** | `SEARCH n USING COVERING INDEX ix_notes_lead_created (lead_id=? AND created_at>?)` |

Output was compared line by line: identical counts for all six counsellors.

## Note for Mr. Fernandes

> The neglected-leads report was checking every note for every lead, which got slower as AdmitFlow grew. I added an index (like a book's index) so it jumps straight to each lead's notes. It now runs in under a hundredth of a second, with exactly the same numbers. Saving notes is unaffected (the index adds a negligible cost per note).

## Prevent the next one

- Index every **foreign key** column (`notes.lead_id`) by default. `SqlRepository` does: see `index=True` in [`db.py`](../../../projects/admitflow/admitflow/db.py).
- Test reports against **realistic volumes** (`make_big_db.py`), not just the 190-lead sample.
- Never wrap an indexed column in a function in `WHERE`; transform the value you compare against instead.
- In PostgreSQL, use `EXPLAIN ANALYZE` and enable slow-query logging (`log_min_duration_statement`) to catch these before users do (Module 10).
