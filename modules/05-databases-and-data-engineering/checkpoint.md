# Module 05 — Checkpoint

Pass mark: **10 / 12**, plus the [build](build.md) and [break & fix](break-and-fix/README.md).

---

**1.** Why does AdmitFlow store channels in a separate `lead_sources` table instead of a `sources` text column like `"website,ad"`?

**2.** Write a query: number of leads per course, only for courses with at least 30 leads, largest first.

**3.** What's the difference between `JOIN` and `LEFT JOIN`? Write a query listing leads that have **no** notes.

**4.** A colleague reports 203 "leads" in total, but there are 190. What probably happened?

**5.** What does this return, and why?
```sql
SELECT COUNT(*) FROM leads WHERE email = NULL;
```

**6.** Write a query returning each lead's **most recent** note (lead_id, text, created_at).

**7.** Why can't the database use an index for `WHERE date(created_at) >= '2026-11-06'`? How do you rewrite it?

**8.** What does a transaction guarantee? Give an AdmitFlow example where not using one would leave bad data.

**9.** What's the N+1 query problem, and how does `selectinload` fix it?

**10.** You need to add a `NOT NULL` column `campus` to `leads`, which has 50,000 rows in production. Describe a safe sequence of migrations and deployments.

**11.** Name the four properties of a trustworthy pipeline from Lesson 06.

**12.** When matching SIS admissions to leads, why not match on phone number alone?

---

<details>
<summary><strong>Answers</strong></summary>

1. First normal form: one value per column. A join table makes "leads via WhatsApp" a simple, indexable equality query, prevents typos and duplicates within the list, and lets you record per-channel facts (order, first seen).
2. `SELECT course, COUNT(*) AS n FROM leads GROUP BY course HAVING COUNT(*) >= 30 ORDER BY n DESC;`
3. `JOIN` keeps only rows with a match on both sides; `LEFT JOIN` keeps every left row, with NULLs when there's no match. `SELECT l.lead_id FROM leads l LEFT JOIN notes n ON n.lead_id = l.lead_id WHERE n.id IS NULL;`
4. They counted after joining `lead_sources` (fan-out): leads with several channels are counted once per channel. Use `COUNT(DISTINCT l.lead_id)`.
5. `0`. `NULL = NULL` is unknown, not true. Use `IS NULL`.
6. `WITH r AS (SELECT n.*, ROW_NUMBER() OVER (PARTITION BY lead_id ORDER BY created_at DESC) rn FROM notes n) SELECT lead_id, text, created_at FROM r WHERE rn = 1;`
7. The function must be computed for every row before comparing, so the index order can't be used. Compare the raw column: `WHERE created_at >= '2026-11-06'` (with a precomputed boundary).
8. All-or-nothing (atomicity), consistency, isolation, durability. Example: loading a 500-row file that fails at row 300 without a transaction leaves 299 rows loaded and no record of the run, and a re-run may then duplicate or skip.
9. Loading N objects with 1 query, then running 1 more query **per object** to load related data (N+1 queries). `selectinload` loads all the related rows in one extra query (`WHERE lead_id IN (…)`).
10. (1) Migration adds `campus` as **nullable**; (2) deploy code that writes it for new leads; (3) backfill existing rows (in batches); (4) a later migration sets `NOT NULL` (plus a default or `CHECK`). Back up and test on a copy of production first.
11. Idempotent, auditable, reconcilable, loud about bad data.
12. Phones are shared (families, a parent's phone used for siblings), so phone alone would merge different students. Require phone **and** matching name, or a stronger key (email).

</details>
