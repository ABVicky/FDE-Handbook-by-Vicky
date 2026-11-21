"""Create a realistic-size practice database: 3 years of AdmitFlow data.

Usage: python3 make_big_db.py big.db     (takes a few seconds; creates a file of roughly 15 MB)
Uses only the Python standard library (sqlite3).
"""
import random
import sqlite3
import sys
from datetime import datetime, timedelta

N_LEADS = 20_000
NOTES_PER_LEAD = (0, 8)
COUNSELLORS = ["priya", "omar", "lucia", "kofi", "mei", "arjun"]
STATUSES = ["new", "contacted", "visit_booked", "applied", "enrolled", "lost"]


def main(path):
    random.seed(42)
    db = sqlite3.connect(path)
    db.executescript(
        """
        DROP TABLE IF EXISTS notes;
        DROP TABLE IF EXISTS leads;
        CREATE TABLE leads (
            lead_id TEXT PRIMARY KEY,
            received_at TEXT NOT NULL,
            name TEXT NOT NULL,
            status TEXT NOT NULL,
            assigned_to TEXT
        );
        CREATE TABLE notes (
            id INTEGER PRIMARY KEY,
            lead_id TEXT NOT NULL REFERENCES leads(lead_id),
            author TEXT NOT NULL,
            text TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        """
    )
    end = datetime(2026, 11, 20)
    leads, notes = [], []
    for i in range(N_LEADS):
        received = end - timedelta(minutes=random.randint(0, 3 * 365 * 24 * 60))
        counsellor = random.choice(COUNSELLORS)
        leads.append((f"L{i:06d}", received.isoformat(" ", "minutes"), f"Student {i}",
                      random.choice(STATUSES), counsellor))
        for _ in range(random.randint(*NOTES_PER_LEAD)):
            when = received + timedelta(minutes=random.randint(10, 60 * 24 * 60))
            notes.append((f"L{i:06d}", counsellor, "Called, left a message", when.isoformat(" ", "seconds")))
    db.executemany("INSERT INTO leads VALUES (?, ?, ?, ?, ?)", leads)
    db.executemany("INSERT INTO notes (lead_id, author, text, created_at) VALUES (?, ?, ?, ?)", notes)
    db.commit()
    print(f"{path}: {len(leads):,} leads, {len(notes):,} notes")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "big.db")
