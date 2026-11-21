# Module 05 — Exercises

| # | Exercise | After lesson | Solution |
| --- | --- | --- | --- |
| 01 | [SQL drills on AdmitFlow data](01-sql-drills.md) | 02–03 | [`solutions/sql_drills.sql`](solutions/sql_drills.sql) + checker [`check_sql_drills.py`](solutions/check_sql_drills.py) |
| 02 | [Model campus visits](02-data-model.md) | 01, 05 | [`solutions/02-data-model.md`](solutions/02-data-model.md) |
| 03 | [An idempotent fee loader with history](03-idempotent-loader.md) | 04, 06 | [`solutions/fee_loader.py`](solutions/fee_loader.py) |

Build the practice database first (needs `admitflow` installed with the `db` extra):

```bash
cd modules/05-databases-and-data-engineering/exercises/solutions
```

```bash
python check_sql_drills.py --db ~/admitflow-practice.db
```
