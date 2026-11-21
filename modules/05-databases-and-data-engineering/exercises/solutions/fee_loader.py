"""Exercise 03 — reference solution: an idempotent fee-schedule loader with history.

Finance sends `fees.csv` every term. Requirements:
* one current fee per (course, campus)
* loading the same file twice changes nothing
* when a fee changes, keep the old value in a history table with the dates it applied
* reject bad rows with reasons, and reconcile counts

Run: python3 fee_loader.py   (self-checking, standard library only)
"""
import csv
import io
import sqlite3
from datetime import date

SCHEMA = """
CREATE TABLE IF NOT EXISTS fees (
    course      TEXT NOT NULL,
    campus      TEXT NOT NULL CHECK (campus IN ('North', 'South')),
    fee_cents   INTEGER NOT NULL CHECK (fee_cents > 0),
    valid_from  TEXT NOT NULL,
    PRIMARY KEY (course, campus)
);
CREATE TABLE IF NOT EXISTS fee_history (
    course      TEXT NOT NULL,
    campus      TEXT NOT NULL,
    fee_cents   INTEGER NOT NULL,
    valid_from  TEXT NOT NULL,
    valid_to    TEXT NOT NULL
);
"""


def parse_fee(text):
    """'1,250.00' or '1250' → 125000 cents. Raises ValueError for anything else."""
    cleaned = text.replace(",", "").strip()
    whole, _, cents = cleaned.partition(".")
    if not whole.isdigit() or (cents and not (cents.isdigit() and len(cents) <= 2)):
        raise ValueError(f"not a fee: {text!r}")
    return int(whole) * 100 + int((cents or "0").ljust(2, "0"))


def load_fees(db, csv_text, effective):
    """Returns (inserted, changed, unchanged, rejected). All in one transaction."""
    inserted = changed = unchanged = 0
    rejected = []
    rows = list(csv.DictReader(io.StringIO(csv_text)))
    with db:  # sqlite3 connection as context manager = one transaction (commit or rollback)
        for line, row in enumerate(rows, start=2):
            try:
                course, campus = row["course"].strip(), row["campus"].strip().title()
                fee = parse_fee(row["fee"])
                if campus not in ("North", "South"):
                    raise ValueError(f"unknown campus {campus!r}")
            except (KeyError, ValueError) as exc:
                rejected.append((line, str(exc)))
                continue
            current = db.execute(
                "SELECT fee_cents, valid_from FROM fees WHERE course = ? AND campus = ?", (course, campus)
            ).fetchone()
            if current is None:
                db.execute("INSERT INTO fees VALUES (?, ?, ?, ?)", (course, campus, fee, effective.isoformat()))
                inserted += 1
            elif current[0] == fee:
                unchanged += 1  # idempotent: same value, nothing to do
            else:
                db.execute("INSERT INTO fee_history VALUES (?, ?, ?, ?, ?)",
                           (course, campus, current[0], current[1], effective.isoformat()))
                db.execute("UPDATE fees SET fee_cents = ?, valid_from = ? WHERE course = ? AND campus = ?",
                           (fee, effective.isoformat(), course, campus))
                changed += 1
    assert inserted + changed + unchanged + len(rejected) == len(rows)  # reconciliation
    return inserted, changed, unchanged, rejected


TERM1 = """course,campus,fee
Accounting,North,"1,250.00"
Accounting,South,1250
Data Analytics,North,1800
Web Development,north,1650.5
Nursing Assistance,East,900
Digital Marketing,South,abc
"""

TERM2 = """course,campus,fee
Accounting,North,1300
Accounting,South,1250
Data Analytics,North,1800
Web Development,North,1650.50
"""

if __name__ == "__main__":
    db = sqlite3.connect(":memory:")
    db.executescript(SCHEMA)

    assert parse_fee("1,250.00") == 125000 and parse_fee("1650.5") == 165050
    first = load_fees(db, TERM1, date(2026, 1, 1))
    assert first[:3] == (4, 0, 0) and [line for line, _ in first[3]] == [6, 7]

    again = load_fees(db, TERM1, date(2026, 1, 1))
    assert again[:3] == (0, 0, 4)                    # idempotent

    second = load_fees(db, TERM2, date(2026, 9, 1))
    assert second[:3] == (0, 1, 3)                   # only Accounting North changed
    assert db.execute("SELECT fee_cents FROM fees WHERE course='Accounting' AND campus='North'").fetchone() == (130000,)
    assert db.execute("SELECT fee_cents, valid_from, valid_to FROM fee_history").fetchall() == [
        (125000, "2026-01-01", "2026-09-01")
    ]
    print("all checks passed")
