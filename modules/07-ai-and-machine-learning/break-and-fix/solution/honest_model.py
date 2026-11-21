"""The same idea, done honestly. Compare with ../amazing_model.py.

Fixes: (1) drop every column not known at enquiry time; (2) split by time (train 2024, test 2025);
(3) compare with trivial baselines; (4) use metrics that fit a 12% base rate.
"""
import warnings
from pathlib import Path

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, roc_auc_score

warnings.filterwarnings("ignore")
DATA = Path(__file__).resolve().parents[4] / "projects" / "admitflow" / "data" / "historical_leads.csv"

df = pd.read_csv(DATA)
# Known only AFTER the enquiry: leakage. (Response time and contacts are things we *do*, not things we *know*.)
LEAKY = ["fee_paid", "days_to_final_status", "hours_to_first_contact", "contacts_first_week"]
df = df.drop(columns=LEAKY)
df["hour"] = pd.to_datetime(df["received_at"]).dt.hour
X_all = pd.get_dummies(df.drop(columns=["lead_id", "received_at", "enrolled"]), columns=["primary_source", "course"])

train = df["intake"] == 2024
X_train, X_test = X_all[train].drop(columns="intake"), X_all[~train].drop(columns="intake")
y_train, y_test = df.loc[train, "enrolled"], df.loc[~train, "enrolled"]

model = RandomForestClassifier(n_estimators=300, min_samples_leaf=20, random_state=1).fit(X_train, y_train)
scores = model.predict_proba(X_test)[:, 1]

always_no = accuracy_score(y_test, [0] * len(y_test))
print(f"'Always predict not enrolled' accuracy: {always_no:.1%}   <- the bar any accuracy claim must clear")
print(f"Honest model accuracy:                  {accuracy_score(y_test, model.predict(X_test)):.1%}")
print(f"Honest model ROC AUC:                   {roc_auc_score(y_test, scores):.3f}   (0.5 = random)")
