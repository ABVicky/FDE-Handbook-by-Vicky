# Module 03 — Exercises

| Set | Covers lessons | Exercises | Solution |
| --- | --- | --- | --- |
| [01 — Basics](01-basics.md) | 02–04 | Types, loops, functions, dates | [`solutions/ex01_basics.py`](solutions/ex01_basics.py) |
| [02 — Collections and strings](02-collections-and-strings.md) | 05–06 | Counting, grouping, cleaning names | [`solutions/ex02_collections.py`](solutions/ex02_collections.py) |
| [03 — Files and errors](03-files-and-errors.md) | 07–08 | CSV → JSON, rejecting bad rows | [`solutions/ex03_files.py`](solutions/ex03_files.py) |
| [04 — Classes and tests](04-classes-and-tests.md) | 10–12 | A `FollowUp` dataclass with tests | [`solutions/ex04_followup.py`](solutions/ex04_followup.py), [`solutions/test_ex04_followup.py`](solutions/test_ex04_followup.py) |
| [05 — APIs and JavaScript](05-apis-and-javascript.md) | 14, 18, 19 | Retrying API client; JS/TS stats | [`solutions/ex05_fetch.py`](solutions/ex05_fetch.py), [`solutions/stats.mjs`](solutions/stats.mjs) |
| [Practice projects](practice-projects.md) | All | CLI task manager, CSV cleaner, API info app | Your own |

## How to use the solutions

Each Python solution file checks itself. Run it from the `solutions/` folder:

```bash
cd modules/03-programming-fundamentals/exercises/solutions
```

```bash
python3 ex01_basics.py
```

It prints `all checks passed` if the reference answers work. Put your own answers in your fork (e.g. `my-work/m03/ex01.py`) and copy the checks at the bottom of the solution file to test them.
