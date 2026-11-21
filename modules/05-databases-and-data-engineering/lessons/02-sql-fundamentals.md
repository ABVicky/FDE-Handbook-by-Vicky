# Lesson 02 — SQL fundamentals

**Time:** ~6 hours · **Core**

## Why this matters

SQL is the most durable skill in this handbook. Client data almost always ends up in a SQL database or warehouse, and being able to answer a stakeholder's question with a query in five minutes, instead of a script in an afternoon, makes you very effective.

## Get a database to practise on

```bash
cd modules/05-databases-and-data-engineering/exercises/solutions
```

```bash
python check_sql_drills.py --db ~/admitflow-practice.db
```

```bash
sqlite3 ~/admitflow-practice.db
```

(Install the `sqlite3` command-line tool with `brew install sqlite` or `sudo apt install sqlite3` if needed, or use a GUI such as DB Browser for SQLite or DBeaver.) Useful sqlite commands: `.tables`, `.schema leads`, `.mode box`, `.quit`.

## SELECT: reading data

```sql
SELECT lead_id, name, course
FROM leads
WHERE status = 'new'
  AND course = 'Accounting'
ORDER BY received_at DESC
LIMIT 10;
```

Logical order of evaluation (useful for understanding errors): `FROM → WHERE → GROUP BY → HAVING → SELECT → ORDER BY → LIMIT`.

### Filtering

```sql
WHERE status IN ('new', 'contacted')
WHERE email IS NULL                 -- never "= NULL"
WHERE name LIKE '%Nguyễn%'          -- pattern match (% = anything)
WHERE received_at >= '2026-09-15' AND received_at < '2026-09-22'   -- half-open range
```

`NULL` means "unknown". `NULL = NULL` is not true. Use `IS NULL` / `IS NOT NULL`.

## Aggregating

```sql
SELECT course,
       COUNT(*)                                             AS leads,
       SUM(CASE WHEN status = 'enrolled' THEN 1 ELSE 0 END) AS enrolled
FROM leads
GROUP BY course
HAVING COUNT(*) >= 20          -- filter groups (WHERE filters rows)
ORDER BY leads DESC;
```

`COUNT(*)` counts rows; `COUNT(email)` counts non-NULL emails. `CASE WHEN` inside `SUM` is the standard way to count a condition.

## Joining tables

```sql
SELECT s.source, COUNT(*) AS leads
FROM leads AS l
JOIN lead_sources AS s ON s.lead_id = l.lead_id
GROUP BY s.source;
```

| Join | Returns |
| --- | --- |
| `JOIN` (inner) | Only rows with a match on both sides |
| `LEFT JOIN` | Every row from the left, with NULLs where the right has no match |
| `FULL OUTER JOIN` | Everything from both (PostgreSQL; SQLite ≥ 3.39) |

**Find things with no match**, e.g. leads with no notes:

```sql
SELECT l.lead_id, l.name
FROM leads AS l
LEFT JOIN notes AS n ON n.lead_id = l.lead_id
WHERE n.id IS NULL;
```

**The fan-out trap:** joining one-to-many multiplies rows. If you join `leads` to `lead_sources` and then `COUNT(*)`, a lead with three channels is counted three times. Sometimes that's what you want (per-channel counts), and sometimes it silently inflates a total. Use `COUNT(DISTINCT l.lead_id)` when you mean unique leads.

## Changing data

```sql
INSERT INTO notes (lead_id, author, text, created_at)
VALUES ('ENQ-0001', 'priya', 'Called', '2026-09-20 10:00');

UPDATE leads SET status = 'contacted' WHERE lead_id = 'ENQ-0001';

DELETE FROM notes WHERE id = 42;
```

⚠️ `UPDATE` or `DELETE` without `WHERE` affects **every row**. Before running one on a client database: run the same `WHERE` as a `SELECT` first, do it inside a transaction (Lesson 04), and have a backup.

## Parameters, never string formatting

From code, **always** pass values as parameters:

```python
db.execute("SELECT * FROM leads WHERE email = ?", (email,))          # ✅
db.execute(f"SELECT * FROM leads WHERE email = '{email}'")           # ❌ SQL injection
```

With the second version, an "email" of `' OR '1'='1` returns every lead. SQLAlchemy parameterizes automatically.

## SQLite vs. PostgreSQL

The SQL above works in both. Differences you'll meet: date functions (`julianday`/`strftime` in SQLite vs `date_trunc`/`age`/`extract` in PostgreSQL), `ILIKE` (PostgreSQL case-insensitive match), stricter typing in PostgreSQL, and concurrency (SQLite allows one writer at a time). Use SQLite for learning and tests; PostgreSQL for anything shared.

## Check yourself

Do drills Q1–Q8 in [Exercise 01](../exercises/01-sql-drills.md) without looking at the answers.

Next: [Lesson 03 — Analytical SQL: CTEs and window functions](03-analytical-sql.md)
