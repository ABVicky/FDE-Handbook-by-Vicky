# Lesson 03 — Analytical SQL: CTEs and window functions

**Time:** ~4 hours · **Core**

## Why this matters

Business questions are rarely single aggregates. "What's the conversion rate by channel, and how is it trending week by week?" or "What's each counsellor's oldest untouched lead?" need multi-step queries. CTEs and window functions make them readable.

## CTEs: name the steps

A **common table expression** (`WITH`) is a named subquery. Write complex queries as a sequence of readable steps:

```sql
WITH enrolled AS (
    SELECT lead_id, received_at, enrolled_on
    FROM leads
    WHERE status = 'enrolled'
),
days_to_enrol AS (
    SELECT lead_id, julianday(enrolled_on) - julianday(received_at) AS days
    FROM enrolled
)
SELECT ROUND(AVG(days), 1) AS avg_days, MIN(days) AS fastest, MAX(days) AS slowest
FROM days_to_enrol;
```

Debug CTEs by selecting from each step on its own.

## Window functions: calculations across related rows

An aggregate collapses rows into one; a **window function** computes across a set of rows *while keeping each row*.

```sql
SELECT lead_id, course, received_at,
       ROW_NUMBER() OVER (PARTITION BY course ORDER BY received_at) AS nth_in_course,
       COUNT(*)     OVER (PARTITION BY course)                      AS course_total
FROM leads;
```

- `PARTITION BY`: the groups (like `GROUP BY`, without collapsing)
- `ORDER BY`: order within each group
- Common functions: `ROW_NUMBER`, `RANK`, `LAG`/`LEAD` (previous/next row), `SUM(...) OVER` (running totals), `AVG(...) OVER` (moving averages)

### Pattern: the latest row per group

The most useful window pattern in practice: each lead's most recent note.

```sql
WITH ranked AS (
    SELECT n.*, ROW_NUMBER() OVER (PARTITION BY lead_id ORDER BY created_at DESC) AS rn
    FROM notes AS n
)
SELECT lead_id, author, text, created_at FROM ranked WHERE rn = 1;
```

### Pattern: running totals and change over time

```sql
WITH weekly AS (
    SELECT strftime('%Y-%W', received_at) AS week, COUNT(*) AS leads
    FROM leads GROUP BY week
)
SELECT week, leads,
       SUM(leads) OVER (ORDER BY week)                  AS running_total,
       leads - LAG(leads) OVER (ORDER BY week)          AS change_vs_last_week
FROM weekly;
```

## A funnel query

Funnels (enquiry → contacted → visit → applied → enrolled) are a staple of FDE reporting:

```sql
SELECT
  COUNT(*)                                                                AS enquiries,
  SUM(CASE WHEN status IN ('contacted','visit_booked','applied','enrolled') THEN 1 ELSE 0 END) AS contacted_or_later,
  SUM(CASE WHEN status IN ('visit_booked','applied','enrolled') THEN 1 ELSE 0 END)            AS visit_or_later,
  SUM(CASE WHEN status IN ('applied','enrolled') THEN 1 ELSE 0 END)                           AS applied_or_later,
  SUM(CASE WHEN status = 'enrolled' THEN 1 ELSE 0 END)                                        AS enrolled
FROM leads;
```

This assumes statuses only move forward. If they can go backwards, you need a **status history** table (`lead_status_changes`) to report the funnel accurately. That's a data-model decision to make early.

## Numbers you can defend

Before you send any number to a client:
- **Reconcile:** does the total match another source (e.g. 22 enrolments here vs. 25 rows in the admissions export, and you can explain the 3 unmatched)?
- **State the definition:** "conversion = enrolled leads ÷ all leads received in September, counting a lead once per channel used."
- **Check for fan-out** (Lesson 02) and NULLs.

## Check yourself

Do drills Q9–Q10. Then write a query that lists, per counsellor, their **oldest lead still in `new` status** and how many days old it is.

Next: [Lesson 04 — Indexes, query plans and transactions](04-indexes-and-transactions.md)
