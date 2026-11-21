"""A contractor's lead-scoring model. Their summary: "99% accurate. Ready for production."

Usage: python amazing_model.py   (needs pandas and scikit-learn)
"""
import warnings
from pathlib import Path

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split

warnings.filterwarnings("ignore")
DATA = Path(__file__).resolve().parents[3] / "projects" / "admitflow" / "data" / "historical_leads.csv"

df = pd.read_csv(DATA)
df["fee_paid"] = (df["fee_paid"] == "Y").astype(int)
df = pd.get_dummies(df, columns=["primary_source", "course"])

X = df.drop(columns=["lead_id", "received_at", "enrolled"])
y = df["enrolled"]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=1)
model = RandomForestClassifier(n_estimators=200, random_state=1).fit(X_train, y_train)

print(f"Accuracy: {accuracy_score(y_test, model.predict(X_test)):.1%}")
top = sorted(zip(model.feature_importances_, X.columns), reverse=True)[:5]
print("Most important features:", ", ".join(name for _, name in top))
