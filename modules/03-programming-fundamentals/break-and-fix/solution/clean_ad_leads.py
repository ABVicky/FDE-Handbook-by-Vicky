"""Clean the ad-platform export before handing it to counsellors (fixed version).

Usage:
    python3 clean_ad_leads.py ../../../../projects/admitflow/data/ad_leads.csv cleaned.csv
"""
import csv
import logging
import sys
import unicodedata

log = logging.getLogger("clean_ad_leads")


def clean_name(raw):
    name = " ".join(unicodedata.normalize("NFC", raw).split())
    # A name is valid if it contains at least one letter in ANY script.
    # str.isalpha() is Unicode-aware: "é", "ễ", "ø", "प" are all letters.
    if not any(ch.isalpha() for ch in name):
        raise ValueError(f"name has no letters: {raw!r}")
    if name.isupper() or name.islower():
        name = name.title()
    return name


def clean_row(row):
    digits = "".join(ch for ch in row["phone_number"] if ch.isdigit())
    return {
        "name": clean_name(row["full_name"]),
        "phone": digits,
        "email": row["email"].strip().lower(),
        "course": row["program_interest"],
    }


def main(src, dst):
    cleaned, rejected = [], []
    with open(src, newline="", encoding="utf-8-sig") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            try:
                cleaned.append(clean_row(row))
            except ValueError as exc:  # only the errors we expect, never a bare `except Exception`
                rejected.append((reader.line_num, str(exc)))
                log.warning("line %d rejected: %s", reader.line_num, exc)

    with open(dst, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=["name", "phone", "email", "course"])
        writer.writeheader()
        writer.writerows(cleaned)

    total = len(cleaned) + len(rejected)
    print(f"Read {total} rows: wrote {len(cleaned)} to {dst}, rejected {len(rejected)}")
    return 1 if rejected else 0


if __name__ == "__main__":
    logging.basicConfig(level=logging.WARNING, format="%(levelname)s %(message)s")
    if len(sys.argv) != 3:
        sys.exit("usage: clean_ad_leads.py SOURCE.csv DEST.csv")
    sys.exit(main(sys.argv[1], sys.argv[2]))
