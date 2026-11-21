"""Clean the ad-platform export before handing it to counsellors.

Written by a previous contractor. Usage:
    python3 clean_ad_leads.py ../../../projects/admitflow/data/ad_leads.csv cleaned.csv
"""
import csv
import re
import sys

VALID_NAME = re.compile(r"^[A-Za-z][A-Za-z .'-]*$")


def clean_row(row):
    name = row["full_name"].strip().title()
    if not VALID_NAME.match(name):
        raise ValueError("invalid name")
    phone = re.sub(r"\D", "", row["phone_number"])
    return {
        "name": name,
        "phone": phone,
        "email": row["email"].strip().lower(),
        "course": row["program_interest"],
    }


def main(src, dst):
    cleaned = []
    with open(src, newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            try:
                cleaned.append(clean_row(row))
            except Exception:
                continue  # skip junk rows

    with open(dst, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=["name", "phone", "email", "course"])
        writer.writeheader()
        writer.writerows(cleaned)
    print(f"Done. Wrote {dst}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
