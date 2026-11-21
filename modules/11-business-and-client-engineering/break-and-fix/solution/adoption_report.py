"""Reference analysis of the usage data: who adopted AdmitFlow, who is drifting, who never started.

Run: python adoption_report.py   (standard library only)
"""
import csv
from collections import defaultdict
from pathlib import Path

rows = list(csv.DictReader(open(Path(__file__).resolve().parent.parent / "evidence" / "usage_weekly.csv")))
notes = defaultdict(dict)
for row in rows:
    notes[row["counsellor"]][int(row["week"])] = int(row["notes_added"])

print(f"{'counsellor':<11}" + "".join(f"w{w:<4}" for w in range(1, 9)) + "trend      group")
groups = {}
for name, weeks in notes.items():
    first, last = sum(weeks[w] for w in (1, 2)) / 2, sum(weeks[w] for w in (7, 8)) / 2
    if first == 0 and last == 0:
        group = "never started"
    elif last >= 0.8 * first and last >= 20:
        group = "adopted"
    elif last < 0.5 * first:
        group = "drifting away"
    else:
        group = "partial"
    groups[name] = group
    trend = "→" if group == "adopted" else ("—" if group == "never started" else "↓")
    print(f"{name:<11}" + "".join(f"{weeks[w]:<5}" for w in range(1, 9)) + f"{trend:<11}{group}")

assert groups == {"priya": "adopted", "omar": "drifting away", "lucia": "drifting away", "kofi": "drifting away",
                  "mei": "never started", "arjun": "adopted"}
print("\n2 of 6 counsellors use AdmitFlow fully; 3 are drifting back to spreadsheets; 1 never started.")
