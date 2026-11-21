"""The 'neglected leads' report: open leads with no note in the 14 days before a date.

Mr. Fernandes runs this every Monday. It used to take a second; now it takes ages.
Usage: python3 slow_report.py big.db
"""
import sqlite3
import sys
import time

AS_OF = "2026-11-20"

QUERY = """
SELECT l.assigned_to AS counsellor, COUNT(*) AS neglected
FROM leads AS l
WHERE l.status IN ('new', 'contacted', 'visit_booked', 'applied')
  AND NOT EXISTS (
      SELECT 1 FROM notes AS n
      WHERE n.lead_id = l.lead_id
        AND date(n.created_at) >= date(?, '-14 days')
  )
GROUP BY l.assigned_to
ORDER BY neglected DESC
"""


def main(path):
    db = sqlite3.connect(path)
    start = time.perf_counter()
    rows = db.execute(QUERY, (AS_OF,)).fetchall()
    elapsed = time.perf_counter() - start
    for counsellor, neglected in rows:
        print(f"{counsellor:<8} {neglected:>6}")
    print(f"\n{elapsed:.2f} seconds")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "big.db")
