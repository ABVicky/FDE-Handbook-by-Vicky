# Lesson 04 — Indexes, query plans and transactions

**Time:** ~4 hours · **Core**

## Why this matters

Two of the most common production problems an FDE gets called about: "the report has become unbearably slow" and "the numbers don't add up after the import crashed." Indexes fix the first; transactions prevent the second.

## Indexes

Without an index, finding rows means reading the whole table (a **scan**). An **index** is a sorted structure (usually a B-tree) that lets the database jump to matching rows, like the index at the back of a book.

```sql
CREATE INDEX ix_notes_lead_created ON notes (lead_id, created_at);
```

Index the columns you **filter, join and sort on**: foreign keys (`notes.lead_id`), common filters (`leads.status`), lookup columns (`leads.email`).

### Composite indexes: order matters

An index on `(lead_id, created_at)` helps:
- `WHERE lead_id = ?` ✅
- `WHERE lead_id = ? AND created_at >= ?` ✅ (best)
- `WHERE created_at >= ?` ❌ (it's sorted by lead_id first)

### Things that stop an index being used

```sql
WHERE date(created_at) >= '2026-11-06'   -- ❌ a function on the column: must compute for every row
WHERE created_at >= '2026-11-06'         -- ✅ compare the raw column to a value
WHERE lower(email) = 'a@b.com'           -- ❌ unless you have an index on lower(email)
WHERE email LIKE '%@example.com'         -- ❌ leading wildcard
```

### Indexes aren't free

Each index slows down inserts and updates slightly and uses disk. Don't index everything; index what queries need, and measure.

## Reading a query plan

Ask the database how it will run a query:

```sql
EXPLAIN QUERY PLAN SELECT ...;   -- SQLite
EXPLAIN ANALYZE SELECT ...;      -- PostgreSQL: actually runs it and shows real timings
```

From this module's break & fix:

```
SCAN l
CORRELATED SCALAR SUBQUERY 1
SCAN n                                   ← reads every note, once per lead!   (26.5 s)
```

After adding the index and removing `date()`:

```
SCAN l
CORRELATED SCALAR SUBQUERY 1
SEARCH n USING COVERING INDEX ix_notes_lead_created (lead_id=? AND created_at>?)   (0.007 s)
```

`SCAN` on a big table inside a loop is the red flag. `SEARCH ... USING INDEX` is what you want. "Covering" means the index alone answered the question, without even reading the table.

## Transactions

A **transaction** groups changes so they happen **all or nothing**:

```sql
BEGIN;
UPDATE leads SET status = 'enrolled', student_no = 'NB260010' WHERE lead_id = 'ENQ-0042';
INSERT INTO notes (lead_id, author, text, created_at) VALUES ('ENQ-0042', 'system', 'Enrolled', '2026-10-10');
COMMIT;      -- or ROLLBACK; to undo everything since BEGIN
```

The **ACID** guarantees:
- **Atomic:** all or nothing
- **Consistent:** constraints hold before and after
- **Isolated:** concurrent transactions don't see each other's half-done work
- **Durable:** once committed, it survives a crash

In SQLAlchemy:

```python
with repo.session() as s, s.begin():   # commits at the end, rolls back on any exception
    for lead in leads:
        ...
```

`SqlRepository.add_leads` loads a whole file in one transaction: if row 3,000 fails, none of the file is half-loaded.

**Keep transactions short.** A transaction left open (say, waiting for a user or an API call) holds locks and blocks other users.

## Concurrency, briefly

Two counsellors update the same lead at once: who wins? Options:
- **Last write wins** (simple; usually fine for status changes)
- **Optimistic locking:** a `version` column; update `WHERE lead_id = ? AND version = ?`, and if 0 rows changed, someone else got there first
- `SELECT ... FOR UPDATE` (PostgreSQL): lock the row while you work on it

## Check yourself

1. Run the [break & fix](../break-and-fix/README.md) and read both query plans yourself.
2. Which indexes does `SqlRepository` define, and which query does each one serve? (Read [`db.py`](../../../projects/admitflow/admitflow/db.py).)

Next: [Lesson 05 — Python and databases: SQLAlchemy and migrations](05-sqlalchemy-and-migrations.md)
