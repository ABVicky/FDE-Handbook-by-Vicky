"""Exercise 03 — reference: turn scores into a business decision under limited capacity.

Counsellors can make 60 first calls a day, but ~90 new leads arrive on peak days. Who goes first?
Compare three policies on the 2025 intake (scores from a model trained on 2024).
"""
import warnings
from pathlib import Path

import pandas as pd

warnings.filterwarnings("ignore")
HERE = Path(__file__).resolve()
DATA = HERE.parents[4] / "projects" / "admitflow" / "data" / "historical_leads.csv"
import sys
sys.path.insert(0, str(HERE.parents[4] / "projects" / "admitflow"))
from admitflow.scoring import features_from_row, train  # noqa: E402

result = train(DATA)
df = pd.read_csv(DATA)
test = df[df.intake == 2025].reset_index(drop=True)
test["score"] = result.model.predict_proba(pd.DataFrame([features_from_row(r) for r in test.astype(str).to_dict("records")]))[:, 1]

CAPACITY = 60 / 90  # fraction of leads that get a call on day 1
k = int(len(test) * CAPACITY)
policies = {
    "random order": test.sample(frac=1, random_state=0).head(k),
    "by score": test.sort_values("score", ascending=False).head(k),
    "first come, first served": test.sort_values("received_at").head(k),
}
print(f"Day-one calls cover {CAPACITY:.0%} of leads ({k} of {len(test)}). Enrolled students reached on day one:")
for name, called in policies.items():
    print(f"  {name:<26} {called.enrolled.sum():>4}  ({called.enrolled.sum() / test.enrolled.sum():.0%} of all who enrolled)")
gain = policies["by score"].enrolled.sum() - policies["random order"].enrolled.sum()
print(f"\nCalling by score reaches ~{gain} more future students on day one than random order,")
print("but the bigger lever is capacity itself: leads not called within 72h almost never enrol.")
assert policies["by score"].enrolled.sum() >= policies["random order"].enrolled.sum()
