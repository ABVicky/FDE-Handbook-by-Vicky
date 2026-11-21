"""Exercise 01 — reference: explore the historical data with pandas. Run: python ex01_explore.py"""
from pathlib import Path

import pandas as pd

DATA = Path(__file__).resolve().parents[4] / "projects" / "admitflow" / "data" / "historical_leads.csv"
df = pd.read_csv(DATA, parse_dates=["received_at"])

print(df.shape, "\n", df.dtypes, "\n")
print("Missing values per column:\n", df.isna().sum()[lambda s: s > 0], "\n")

base_rate = df["enrolled"].mean()
by_source = df.groupby("primary_source")["enrolled"].agg(["count", "mean"]).sort_values("mean", ascending=False)
by_intake = df.groupby("intake")["enrolled"].mean()
df["response_bucket"] = pd.cut(df["hours_to_first_contact"], [0, 1, 24, 72, float("inf")],
                               labels=["<1h", "1-24h", "24-72h", ">72h"], right=False)
by_response = df.groupby("response_bucket", observed=True)["enrolled"].agg(["count", "mean"])
office = df["received_at"].dt.weekday.lt(5) & df["received_at"].dt.hour.between(9, 17)
by_office = df.groupby(office)["hours_to_first_contact"].median()

print(f"Base rate: {base_rate:.1%}\n\nBy source:\n{by_source}\n\nBy intake:\n{by_intake}\n")
print(f"By response time:\n{by_response}\n\nMedian hours to first contact (office hours?):\n{by_office}")

assert len(df) == 3000 and 0.10 < base_rate < 0.14
assert by_source.index[0] == "walk-in"                       # highest-converting source
assert by_response.loc[">72h", "mean"] < 0.05                # leads left >3 days rarely enrol
assert by_office[False] > by_office[True] * 2                 # out-of-hours enquiries wait much longer
print("\nall checks passed")
