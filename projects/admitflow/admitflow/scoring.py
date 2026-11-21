"""Lead scoring: how likely is a new enquiry to enrol? (added in Module 07)

Design decisions (see docs/adr/004-lead-scoring.md):
* Only features **known at enquiry time** (no response time, no fee status: those are leakage).
* Train on an older intake, test on a newer one (a temporal split mirrors real use).
* Always compare with a simple baseline; ship the model only if it clearly beats it.
* Logistic regression: good enough, fast, and each prediction can be explained.
* The score ranks who to call first. It never decides who gets called at all.
"""
from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Sequence

CATEGORICAL = ["primary_source", "course"]
NUMERIC = ["extra_channels", "has_email", "has_phone", "out_of_hours"]
FEATURES = CATEGORICAL + NUMERIC
MODEL_VERSION = "lead-score-1"


def out_of_hours(received_at: datetime) -> int:
    """Enquiries outside office hours (weekday 09:00–18:00) wait longer for a first call."""
    return int(not (received_at.weekday() < 5 and 9 <= received_at.hour < 18))


def features_from_row(row: Dict[str, str]) -> Dict[str, object]:
    return {
        "primary_source": row["primary_source"],
        "course": row["course"],
        "extra_channels": int(row["n_channels"]) - 1,   # 0 for the usual single-channel enquiry
        "has_email": int(row["has_email"]),
        "has_phone": int(row["has_phone"]),
        "out_of_hours": out_of_hours(datetime.fromisoformat(row["received_at"])),
    }


def features_from_lead(lead) -> Dict[str, object]:
    primary = lead.sources[0] if lead.sources else "unknown"
    # Walk-in forms record only a date, so received_at is midnight. Walk-ins happen during
    # opening hours by definition: don't let a missing time masquerade as "out of hours".
    date_only = primary == "walk-in" and lead.received_at.hour == 0 and lead.received_at.minute == 0
    return {
        "primary_source": primary,
        "course": lead.course or "unknown",
        "extra_channels": max(len(lead.sources) - 1, 0),
        "has_email": int(bool(lead.email)),
        "has_phone": int(bool(lead.phone)),
        "out_of_hours": 0 if date_only else out_of_hours(lead.received_at),
    }


def load_history(path: Path) -> List[Dict[str, str]]:
    with open(path, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


# -- the baseline: historical conversion rate of each source ---------------------------

class SourceRateBaseline:
    """The 'model' a spreadsheet user would build: score = past conversion rate of the lead's source."""

    def fit(self, X: List[Dict[str, object]], y: Sequence[int]) -> "SourceRateBaseline":
        totals: Dict[str, List[int]] = {}
        for features, label in zip(X, y):
            totals.setdefault(features["primary_source"], [0, 0])
            totals[features["primary_source"]][0] += 1
            totals[features["primary_source"]][1] += label
        self.overall = sum(y) / len(y)
        self.rates = {source: hits / n for source, (n, hits) in totals.items()}
        return self

    def predict_proba(self, X: List[Dict[str, object]]) -> List[float]:
        return [self.rates.get(features["primary_source"], self.overall) for features in X]


# -- the model ------------------------------------------------------------------------

def build_pipeline():
    from sklearn.compose import ColumnTransformer
    from sklearn.linear_model import LogisticRegression
    from sklearn.pipeline import Pipeline
    from sklearn.preprocessing import OneHotEncoder

    preprocess = ColumnTransformer(
        [("categorical", OneHotEncoder(handle_unknown="ignore"), CATEGORICAL), ("numeric", "passthrough", NUMERIC)]
    )
    return Pipeline([("features", preprocess), ("model", LogisticRegression(max_iter=1000, C=1.0))])


def _frame(X: List[Dict[str, object]]):
    import pandas as pd

    return pd.DataFrame(X, columns=FEATURES)


def precision_at_k(y_true: Sequence[int], scores: Sequence[float], fraction: float) -> float:
    """Of the top `fraction` of leads by score, how many enrolled? (What counsellors experience.)"""
    k = max(1, int(len(scores) * fraction))
    ranked = sorted(zip(scores, y_true), key=lambda pair: pair[0], reverse=True)[:k]
    return sum(label for _, label in ranked) / k


def evaluate(y_true: Sequence[int], scores: Sequence[float]) -> Dict[str, float]:
    from sklearn.metrics import brier_score_loss, roc_auc_score

    return {
        "roc_auc": round(float(roc_auc_score(y_true, scores)), 3),
        "precision_at_20pct": round(precision_at_k(y_true, scores, 0.20), 3),
        "brier": round(float(brier_score_loss(y_true, scores)), 4),  # calibration + accuracy of probabilities
        "base_rate": round(sum(y_true) / len(y_true), 3),
    }


@dataclass
class TrainResult:
    model: object
    metrics: Dict[str, Dict[str, float]]
    train_rows: int
    test_rows: int


def train(history_path: Path, train_intakes=("2024",), test_intakes=("2025",)) -> TrainResult:
    rows = load_history(history_path)
    train_rows = [r for r in rows if r["intake"] in train_intakes]
    test_rows = [r for r in rows if r["intake"] in test_intakes]
    X_train = [features_from_row(r) for r in train_rows]
    X_test = [features_from_row(r) for r in test_rows]
    y_train = [int(r["enrolled"]) for r in train_rows]
    y_test = [int(r["enrolled"]) for r in test_rows]

    baseline = SourceRateBaseline().fit(X_train, y_train)
    model = build_pipeline().fit(_frame(X_train), y_train)

    metrics = {
        "baseline": evaluate(y_test, baseline.predict_proba(X_test)),
        "model": evaluate(y_test, model.predict_proba(_frame(X_test))[:, 1]),
    }
    return TrainResult(model, metrics, len(train_rows), len(test_rows))


# -- saving, loading, predicting --------------------------------------------------------

def save(result: TrainResult, path: Path) -> None:
    import joblib

    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(result.model, path)
    path.with_suffix(".json").write_text(
        json.dumps(
            {
                "version": MODEL_VERSION,
                "trained_at": datetime.now().isoformat(timespec="seconds"),
                "features": FEATURES,
                "train_rows": result.train_rows,
                "test_rows": result.test_rows,
                "metrics": result.metrics,
            },
            indent=2,
        ),
        encoding="utf-8",
    )


@dataclass
class Score:
    probability: float
    band: str                   # "high" / "medium" / "low": what counsellors see
    factors: List[str]          # human-readable reasons, strongest first
    model_version: str


class LeadScorer:
    def __init__(self, path: Path):
        import joblib

        self.model = joblib.load(path)
        meta_path = Path(path).with_suffix(".json")
        self.meta = json.loads(meta_path.read_text(encoding="utf-8")) if meta_path.exists() else {}
        self.version = self.meta.get("version", "unknown")
        base_rate = self.meta.get("metrics", {}).get("model", {}).get("base_rate", 0.12)
        self.high, self.low = base_rate * 1.5, base_rate * 0.6

    def _explain(self, features: Dict[str, object], top: int = 3) -> List[str]:
        """For logistic regression, each feature adds (coefficient × value) to the log-odds."""
        preprocess = self.model.named_steps["features"]
        coefs = self.model.named_steps["model"].coef_[0]
        values = preprocess.transform(_frame([features]))
        values = values.toarray()[0] if hasattr(values, "toarray") else values[0]
        names = preprocess.get_feature_names_out()
        contributions = [
            (coef * value, name) for coef, value, name in zip(coefs, values, names) if value != 0
        ]
        contributions.sort(key=lambda item: abs(item[0]), reverse=True)
        return [f"{'+' if c > 0 else '−'} {_readable(name)}" for c, name in contributions[:top]]

    def score(self, lead) -> Score:
        features = features_from_lead(lead)
        probability = float(self.model.predict_proba(_frame([features]))[0, 1])
        band = "high" if probability >= self.high else "low" if probability <= self.low else "medium"
        return Score(round(probability, 3), band, self._explain(features), self.version)


def _readable(name: str) -> str:
    name = name.split("__", 1)[-1]
    for prefix, label in (("primary_source_", "came via "), ("course_", "course: ")):
        if name.startswith(prefix):
            return label + name[len(prefix):]
    return {
        "extra_channels": "enquired through several channels",
        "has_email": "gave an email address",
        "has_phone": "gave a phone number",
        "out_of_hours": "enquired outside office hours",
    }.get(name, name)


def conversion_by_response_time(history_path: Path) -> List[Dict[str, object]]:
    """Descriptive analysis (not a model): enrolment rate by how quickly the first call happened.

    This is often the most actionable finding for the client: response speed is a lever they control.
    It's correlation, not proof of cause. Other factors (e.g. out-of-hours enquiries) differ between buckets.
    """
    buckets = [("under 1 hour", 0, 1), ("1–24 hours", 1, 24), ("24–72 hours", 24, 72), ("over 72 hours", 72, 1e9)]
    rows = load_history(history_path)
    result = []
    for label, low, high in buckets:
        selected = [r for r in rows if low <= float(r["hours_to_first_contact"]) < high]
        enrolled = sum(int(r["enrolled"]) for r in selected)
        result.append({"bucket": label, "leads": len(selected), "enrolled": enrolled,
                       "rate": round(enrolled / len(selected), 3) if selected else 0.0})
    return result


def load_scorer(path: Optional[Path]) -> Optional[LeadScorer]:
    if path is None or not Path(path).exists():
        return None
    return LeadScorer(Path(path))
