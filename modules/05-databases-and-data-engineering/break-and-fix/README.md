# Module 05 — Break & Fix: The Monday report that takes forever

**Time:** 1–2 hours · Do this after [Lesson 04](../lessons/04-indexes-and-transactions.md).

## The situation

Every Monday, Mr. Fernandes runs the **neglected leads** report: for each counsellor, how many open leads have had no note in the last 14 days. When AdmitFlow was new it took under a second. Three years and 20,000 leads later:

> "The report takes nearly half a minute and sometimes the dashboard freezes while it runs. Can you look at it?"

## Setup

Create a realistic-size practice database (standard library only, takes a few seconds):

```bash
cd modules/05-databases-and-data-engineering/break-and-fix
```

```bash
python3 make_big_db.py big.db
```

Run the report:

```bash
python3 slow_report.py big.db
```

Note the time. (On the author's machine: about 26 seconds.)

## Your job

1. **Measure, don't guess.** Get the query plan:
   ```bash
   sqlite3 big.db
   ```
   Then paste `EXPLAIN QUERY PLAN` followed by the query from `slow_report.py`, using `'2026-11-20'` in place of `?`.
2. **Explain** in plain words why it's slow. How many times is the `notes` table read?
3. **Fix it**, keeping the results **exactly the same**. Save the corrected query and any schema change.
4. **Prove it:** before/after timings, before/after query plans, and a comparison showing identical output.
5. **Write a 4-line note** for Mr. Fernandes: what was wrong, what you changed, the new run time, and whether anything else is affected.

## Hints

<details><summary>Hint 1</summary>Look for <code>SCAN n</code> inside <code>CORRELATED SCALAR SUBQUERY</code>. "Correlated" means it runs once per outer row.</details>

<details><summary>Hint 2</summary>What would let the database jump straight to one lead's notes? Which two columns does the subquery filter on?</details>

<details><summary>Hint 3</summary>Even with the right index, <code>date(n.created_at)</code> forces a computation per row. The dates are stored as ISO text, which sorts correctly. What can you compare <code>created_at</code> to directly?</details>

When you're done: [SOLUTION.md](SOLUTION.md)
