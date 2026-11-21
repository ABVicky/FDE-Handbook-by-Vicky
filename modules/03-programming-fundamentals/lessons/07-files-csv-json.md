# Lesson 07 — Files, CSV and JSON

**Time:** ~4 hours · **Core**

## Why this matters

CSV and JSON are the formats you'll exchange with clients most often: exports from CRMs and ad platforms (CSV), and almost every API (JSON). Reading them *correctly* is the foundation of every pipeline you'll build.

## Reading and writing text files

```python
from pathlib import Path

path = Path("notes.txt")
path.write_text("first line\n", encoding="utf-8")

with open(path, "a", encoding="utf-8") as fh:   # "a" = append, "w" = overwrite, "r" = read
    fh.write("second line\n")

with open(path, encoding="utf-8") as fh:
    for line in fh:
        print(line.rstrip("\n"))
```

`with` closes the file automatically, even if an error happens.

`pathlib.Path` is the modern way to handle paths:

```python
data_dir = Path("projects/admitflow/data")
csv_path = data_dir / "leads_sample.csv"   # joins correctly on every OS
csv_path.exists(), csv_path.suffix, csv_path.name
list(data_dir.glob("*.csv"))
```

## CSV: always use the csv module

In Module 02 you saw `split(",")` break on `"Lee, Chloe"`. The `csv` module handles quoting, embedded commas and newlines correctly:

```python
import csv

with open("projects/admitflow/data/leads_sample.csv", newline="", encoding="utf-8") as fh:
    reader = csv.DictReader(fh)          # each row becomes a dict keyed by the header
    for row in reader:
        if not row["enquiry_id"]:        # blank line → all values empty
            continue
        print(row["name"], "|", row["source"])
```

Note `newline=""`: the csv module needs it to handle line endings correctly.

Writing:

```python
rows = [{"name": "Zoë Müller", "course": "Web Development"}]
with open("out.csv", "w", newline="", encoding="utf-8") as fh:
    writer = csv.DictWriter(fh, fieldnames=["name", "course"])
    writer.writeheader()
    writer.writerows(rows)
```

**Excel tip:** if counsellors will open your CSV in Excel, write it with `encoding="utf-8-sig"` so names like `Nguyễn` display correctly.

## Every export is different

Look at the three AdmitFlow files side by side:

| | `leads_sample.csv` | `ad_leads.csv` | `walkins.csv` |
| --- | --- | --- | --- |
| ID column | `enquiry_id` | `lead_id` | none |
| Date format | `2026-09-01 10:55` | `2026-09-01T12:26:00Z` | `04/09/2026` (day first!) |
| Phone | `+1 202-555-0141` | `(202) 555-0141`, `2025550141`, … | in a shared `Contact` column with emails |
| Course | full names | codes like `web_dev` | abbreviations like `DA`, `BBA` |
| Quirks | blank lines, quoted names | mixed-case emails | BOM, ALL-CAPS names, extra spaces |

The FDE approach: one small reader per format, all producing the **same** cleaned structure. That's exactly how [`importers.py`](../../../projects/admitflow/admitflow/importers.py) is organized.

**Dates:** parse them explicitly, with the format written out:

```python
from datetime import datetime
datetime.strptime("04/09/2026", "%d/%m/%Y")   # 4 September 2026, not 9 April
```

Never guess between day-first and month-first. Ask the client which one their system uses.

## JSON

JSON maps naturally onto Python dicts and lists:

```python
import json

lead = {"id": "ENQ-0001", "name": "Zoë Müller", "sources": ["ad", "website"]}

text = json.dumps(lead, ensure_ascii=False, indent=2)   # to a string
back = json.loads(text)                                 # from a string

with open("leads.json", "w", encoding="utf-8") as fh:
    json.dump([lead], fh, ensure_ascii=False, indent=2)
with open("leads.json", encoding="utf-8") as fh:
    leads = json.load(fh)
```

| JSON | Python |
| --- | --- |
| object `{}` | `dict` |
| array `[]` | `list` |
| string, number | `str`, `int`/`float` |
| `true`/`false`/`null` | `True`/`False`/`None` |

JSON has no date type, so store dates as ISO 8601 strings (`"2026-09-01T10:55"`), as the AdmitFlow store does.

## Check yourself

Write a script that reads `ad_leads.csv` with `csv.DictReader` and writes a JSON file containing a list of `{"name", "course", "campaign"}` dicts, one per lead. Check that `Nguyễn` appears correctly when you open the JSON in your editor.

Next: [Lesson 08 — Errors, exceptions and logging](08-errors-and-logging.md)
