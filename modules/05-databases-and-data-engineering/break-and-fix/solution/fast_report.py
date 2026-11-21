"""The 'neglected leads' report, fixed.

Two changes (see SOLUTION.md):
1. An index on notes(lead_id, created_at), so each lead's notes are found directly.
2. Compare the raw column against a precomputed value instead of wrapping it in date(),
   so the index can be used for the date range too.
Usage: python3 fast_report.py big.db
"""
import sqlite3
import sys
import time
from datetime import date, timedelta

AS_OF = date(2026, 11, 20)

QUERY = """
SELECT l.assigned_to AS counsellor, COUNT(*) AS neglected
FROM leads AS l
WHERE l.status IN ('new', 'contacted', 'visit_booked', 'applied')
  AND NOT EXISTS (
      SELECT 1 FROM notes AS n
      WHERE n.lead_id = l.lead_id
        AND n.created_at >= ?
  )
GROUP BY l.assigned_to
ORDER BY neglected DESC
"""


def main(path):
    db = sqlite3.connect(path)
    db.execute("CREATE INDEX IF NOT EXISTS ix_notes_lead_created ON notes (lead_id, created_at)")
    since = (AS_OF - timedelta(days=14)).isoformat()      # '2026-11-06' sorts correctly as text
    start = time.perf_counter()
    rows = db.execute(QUERY, (since,)).fetchall()
    elapsed = time.perf_counter() - start
    for counsellor, neglected in rows:
        print(f"{counsellor:<8} {neglected:>6}")
    print(f"\n{elapsed:.3f} seconds")
    for row in db.execute("EXPLAIN QUERY PLAN " + QUERY, (since,)):
        print("plan:", row[3])


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "big.db")
