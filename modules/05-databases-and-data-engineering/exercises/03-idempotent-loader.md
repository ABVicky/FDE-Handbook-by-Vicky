# Exercise 03 — An idempotent fee loader with history

Finance emails `fees.csv` each term: `course,campus,fee`, with fees written like `1,250.00`, `1250` or `1650.5`, and occasional mistakes.

Write `load_fees(db, csv_text, effective_date)` using only `sqlite3`:

- Table `fees`: one **current** fee per `(course, campus)`, stored in **cents** as an integer, with `valid_from`
- Table `fee_history`: when a fee changes, keep the old value with `valid_from` and `valid_to`
- Loading the **same file twice changes nothing**
- Bad rows (unknown campus, unparsable fee) are **rejected with line numbers and reasons**
- Everything in **one transaction**
- Returns `(inserted, changed, unchanged, rejected)` and asserts they reconcile with the row count

Test it with two terms of data where one fee changes. The solution file includes sample CSVs and checks.

**Why this matters later:** in Module 08 the AI assistant answers questions about fees. If it reads an outdated fee schedule, it quotes the wrong price, which is that module's break & fix. Knowing which fee is current, and since when, is a data problem before it's an AI problem.
