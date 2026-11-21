"""Exercise 02 — reference: compare baseline, logistic regression and a tree model, honestly."""
import warnings
from pathlib import Path

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

warnings.filterwarnings("ignore")
DATA = Path(__file__).resolve().parents[4] / "projects" / "admitflow" / "data" / "historical_leads.csv"

df = pd.read_csv(DATA, parse_dates=["received_at"])
df["extra_channels"] = df["n_channels"] - 1
df["out_of_hours"] = (~(df["received_at"].dt.weekday.lt(5) & df["received_at"].dt.hour.between(9, 17))).astype(int)
CAT, NUM = ["primary_source", "course"], ["extra_channels", "has_email", "has_phone", "out_of_hours"]

train, test = df[df.intake == 2024], df[df.intake == 2025]          # temporal split
y_train, y_test = train["enrolled"], test["enrolled"]


def precision_at(scores, y, fraction=0.2):
    k = int(len(scores) * fraction)
    return y.iloc[pd.Series(scores).sort_values(ascending=False).index[:k]].mean()


def pipeline(model):
    pre = ColumnTransformer([("cat", OneHotEncoder(handle_unknown="ignore"), CAT), ("num", "passthrough", NUM)])
    return Pipeline([("pre", pre), ("model", model)])


results = {}
rates = train.groupby("primary_source")["enrolled"].mean()
results["baseline (source rate)"] = test["primary_source"].map(rates).fillna(y_train.mean()).to_numpy()
for name, model in [("logistic regression", LogisticRegression(max_iter=1000)),
                    ("gradient boosting", GradientBoostingClassifier(random_state=0, max_depth=2, n_estimators=150))]:
    results[name] = pipeline(model).fit(train[CAT + NUM], y_train).predict_proba(test[CAT + NUM])[:, 1]

y_test = y_test.reset_index(drop=True)
print(f"{'model':<24} {'ROC AUC':>8} {'prec@20%':>9}   (test base rate {y_test.mean():.1%})")
for name, scores in results.items():
    print(f"{name:<24} {roc_auc_score(y_test, scores):>8.3f} {precision_at(scores, y_test):>9.3f}")

aucs = {name: roc_auc_score(y_test, s) for name, s in results.items()}
assert max(aucs.values()) - min(aucs.values()) < 0.06   # no model is dramatically better: the data limits us
print("\nConclusion: a fancier model doesn't help much here. The signal isn't in these features.")
