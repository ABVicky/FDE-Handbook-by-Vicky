# Exercise 02 — Model campus visits

Using the campus-visits requirements from [Module 04, Exercise 01](../../04-software-engineering/exercises/01-api-design.md):

1. Draw an ERD (Mermaid `erDiagram`) adding the new table(s) to AdmitFlow's model.
2. Write the `CREATE TABLE` statements with types, keys, foreign keys, `NOT NULL`, `CHECK` and `UNIQUE` constraints.
3. List the indexes you'd add, and which query each serves.
4. How would you enforce "at most 8 visits per campus per hour slot"? Compare doing it in SQL vs. in application code, including what happens when two counsellors book the last slot at the same moment.
5. *(stretch)* Add the table to `admitflow/db.py`, generate an Alembic migration, and review it.
