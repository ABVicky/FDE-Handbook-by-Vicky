# Exercise set 03 — Files and errors

Use the real files in `projects/admitflow/data/`.

1. **`ads_to_json(csv_path, json_path)`**: read `ad_leads.csv` with `csv.DictReader` and write a JSON list of `{"name", "course", "campaign"}`. Return the number of records written. Open the JSON and confirm `Nguyễn` and `प्रिया` appear correctly (use `ensure_ascii=False`).
2. **`read_walkin_dates(csv_path)`**: read `walkins.csv` and return a list of `datetime` objects from the `Date` column (day first!). First try `encoding="utf-8"`. What error do you get, and why? Then fix it.
3. **`parse_rows(rows)`**: given a list of dicts with a `"seats"` value, return `(parsed, rejected)`, where `parsed` is a list of ints and `rejected` is a list of `(index, reason)`. Catch only `ValueError`. Test it with `[{"seats": "30"}, {"seats": "thirty"}, {"seats": ""}, {"seats": "12"}]`. You should get 2 parsed and 2 rejected, and `len(parsed) + len(rejected) == len(rows)`.
4. **Logging:** add `logging` to `parse_rows` so that each rejection logs a WARNING with the index and reason. Run it at level INFO, then at level ERROR. What changes?
5. **Explain** in a comment why `except Exception: pass` would be dangerous in `parse_rows`, with a concrete example of a bug it would hide (hint: what if the column were renamed `"Seats"`?).
