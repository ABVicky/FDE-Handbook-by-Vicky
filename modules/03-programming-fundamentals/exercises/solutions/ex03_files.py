"""Exercise set 03 — reference solutions. Run: python3 ex03_files.py"""
import csv
import json
import logging
import tempfile
from datetime import datetime
from pathlib import Path

DATA = Path(__file__).resolve().parents[4] / "projects" / "admitflow" / "data"
log = logging.getLogger("ex03")


def ads_to_json(csv_path, json_path):
    with open(csv_path, newline="", encoding="utf-8") as fh:
        records = [
            {"name": row["full_name"], "course": row["program_interest"], "campaign": row["campaign_name"]}
            for row in csv.DictReader(fh)
        ]
    with open(json_path, "w", encoding="utf-8") as fh:
        json.dump(records, fh, ensure_ascii=False, indent=2)
    return len(records)


def read_walkin_dates(csv_path):
    # With encoding="utf-8" the first header is "﻿Date" (Excel's byte-order mark),
    # so row["Date"] raises KeyError. "utf-8-sig" strips the BOM.
    with open(csv_path, newline="", encoding="utf-8-sig") as fh:
        return [datetime.strptime(row["Date"], "%d/%m/%Y") for row in csv.DictReader(fh)]


def parse_rows(rows):
    parsed, rejected = [], []
    for index, row in enumerate(rows):
        try:
            parsed.append(int(row["seats"]))
        except ValueError as exc:
            rejected.append((index, str(exc)))
            log.warning("row %d rejected: %s", index, exc)
    return parsed, rejected


# 5. If the column were renamed "Seats", row["seats"] raises KeyError on EVERY row.
#    `except Exception: pass` would swallow it: the function would return an empty
#    list, no error, and the report would quietly say "0 seats". Catching only
#    ValueError lets the KeyError crash loudly so someone fixes the column name.


if __name__ == "__main__":
    logging.basicConfig(level=logging.ERROR)
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "ads.json"
        assert ads_to_json(DATA / "ad_leads.csv", out) == 60
        text = out.read_text(encoding="utf-8")
        assert "Nguyễn" in text and "प्रिया" in text
    dates = read_walkin_dates(DATA / "walkins.csv")
    assert len(dates) == 25
    assert dates[0] == datetime(2026, 9, 4)  # "04/09/2026" is 4 September, not 9 April
    assert all(datetime(2026, 9, 1) <= d <= datetime(2026, 10, 31) for d in dates)
    rows = [{"seats": "30"}, {"seats": "thirty"}, {"seats": ""}, {"seats": "12"}]
    parsed, rejected = parse_rows(rows)
    assert parsed == [30, 12] and [i for i, _ in rejected] == [1, 2]
    assert len(parsed) + len(rejected) == len(rows)
    try:
        parse_rows([{"Seats": "30"}])
        raise AssertionError("expected KeyError to propagate")
    except KeyError:
        pass
    print("all checks passed")
