"""Build the AdmitFlow practice database and run the reference SQL answers.

Usage (from this folder, with the admitflow package installed with the `db` extra):
    python check_sql_drills.py            # prints each answer
    python check_sql_drills.py --db my.db # also keeps the database so you can query it yourself
"""
import argparse
import sqlite3
import tempfile
from pathlib import Path

from admitflow.db import SqlRepository
from admitflow.pipeline import ingest, match_admissions

HERE = Path(__file__).resolve().parent
DATA = HERE.parents[3] / "projects" / "admitflow" / "data"


def build(path: Path) -> None:
    repo = SqlRepository(f"sqlite:///{path}", create_tables=True)
    for name, fmt in [("leads_sample.csv", "website"), ("ad_leads.csv", "ads"), ("walkins.csv", "walkins")]:
        ingest(repo, DATA / name, fmt)
    match_admissions(repo, DATA / "admissions_export.csv")


def queries():
    blocks = (HERE / "sql_drills.sql").read_text(encoding="utf-8").split("-- Q")[1:]
    for block in blocks:
        title, _, sql = block.partition("\n")
        yield "Q" + title.strip(), sql.strip()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", help="keep the practice database at this path")
    args = parser.parse_args()
    path = Path(args.db) if args.db else Path(tempfile.mkdtemp()) / "practice.db"
    if path.exists():
        path.unlink()
    build(path)
    db = sqlite3.connect(path)
    results = {}
    for title, sql in queries():
        rows = db.execute(sql).fetchall()
        results[title.split()[0].rstrip(":")] = rows
        print(f"\n{title}\n  " + "\n  ".join(map(str, rows[:8])) + (f"\n  … {len(rows)} rows" if len(rows) > 8 else ""))
    # Sanity checks on known facts about the sample data
    assert results["Q1"] == [(190,)]
    assert sum(n for _, n in results["Q5"]) == 203
    assert len(results["Q6"]) == 11
    assert dict(results["Q2"])["enrolled"] == 22
    assert results["Q10"][-1][2] == 190
    print("\nall checks passed")


if __name__ == "__main__":
    main()
