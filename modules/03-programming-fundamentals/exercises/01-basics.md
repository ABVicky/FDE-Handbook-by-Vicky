# Exercise set 01 — Basics

Write each as a function in `my-work/m03/ex01.py`.

1. **`priority(hours_waiting)`**: return `"urgent"` (> 48), `"high"` (> 24) or `"normal"`. Negative hours should raise `ValueError`.
2. **`hours_between(start, end)`**: both strings like `"2026-09-01 10:00"`; return hours as a float. `hours_between("2026-09-01 10:00", "2026-09-02 16:30")` → `30.5`.
3. **`followup_schedule(days)`**: print the numbers 1 to `days`; print `"follow up"` instead of every multiple of 7; stop entirely at 25. Return the list of printed values.
4. **`late_count(waits, limit=24)`**: number of values in `waits` strictly greater than `limit`, using a loop (not `sum`).
5. **`format_rate(admissions, enquiries)`**: return a string like `"9.1%"`. If `enquiries` is 0, return `"n/a"`.
6. **Predict, then check:** what do `bool("False")`, `"5" * 3`, `7 // 2`, `0.1 + 0.2 == 0.3` evaluate to? Write a comment explaining each.
