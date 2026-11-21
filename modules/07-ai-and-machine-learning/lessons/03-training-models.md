# Lesson 03 — Training models with scikit-learn

**Time:** ~5 hours · **Core**

```bash
python -m pip install "scikit-learn>=1.5" pandas joblib
```

(Or `pip install -e ".[ml]"` in `projects/admitflow`.)

## Pipelines: preprocessing + model as one object

```python
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

CATEGORICAL = ["primary_source", "course"]
NUMERIC = ["extra_channels", "has_email", "has_phone", "out_of_hours"]

pipeline = Pipeline([
    ("features", ColumnTransformer([
        ("categorical", OneHotEncoder(handle_unknown="ignore"), CATEGORICAL),
        ("numeric", "passthrough", NUMERIC),
    ])),
    ("model", LogisticRegression(max_iter=1000)),
])

pipeline.fit(X_train, y_train)
probabilities = pipeline.predict_proba(X_test)[:, 1]
```

Why a pipeline:
- Preprocessing is **learned from training data only**, which prevents contamination.
- The saved object contains everything needed to score a new lead.
- `handle_unknown="ignore"`: a course the model never saw doesn't crash it.

## Models worth knowing

| Model | How it works (intuition) | Strengths | Weaknesses |
| --- | --- | --- | --- |
| **Logistic regression** | Weighted sum of features → probability | Fast, stable, explainable, good with little data | Misses interactions unless you add them |
| **Decision tree** | A flowchart of yes/no questions | Easy to read | Overfits easily |
| **Random forest** | Many trees voting | Strong default, little tuning | Less explainable, larger |
| **Gradient boosting** (sklearn, XGBoost, LightGBM) | Trees added one by one to fix errors | Often the best on tabular data | Needs care to avoid overfitting |

Start with logistic regression. Move to trees or boosting only if they clearly win on your validation data. In AdmitFlow's case they don't ([Exercise 02](../exercises/02-compare-models.md)): the data, not the algorithm, is the limit.

## Overfitting and underfitting

- **Overfitting:** learns noise in the training data; great on train, poor on test.
- **Underfitting:** too simple to capture real patterns; poor on both.

Compare training and test scores. A big gap means overfitting. Fix it with simpler models, regularization (`C` in logistic regression, `min_samples_leaf` in trees), or more data.

## Cross-validation

When data is limited, `cross_val_score` trains and tests on several splits and averages them, giving a steadier estimate for **choosing between options**. Keep a final, untouched test set (for AdmitFlow, the 2025 intake) for the honest final number.

## The AdmitFlow implementation

[`admitflow/scoring.py`](../../../projects/admitflow/admitflow/scoring.py):

```bash
admitflow train-model data/historical_leads.csv --out models/lead_score.joblib
```

```
            ROC AUC  prec@20%   Brier
baseline      0.609     0.143  0.0949
model         0.605     0.157  0.0942

enrolment rate by time to first contact (descriptive, all history):
  under 1 hour     159 leads  14.5%
  1–24 hours      1580 leads  16.3%
  24–72 hours      734 leads  8.4%
  over 72 hours    527 leads  2.5%
```

Lesson 04 explains each number, and why this result leads to the decision in [ADR-004](../../../projects/admitflow/docs/adr/004-lead-scoring.md).

## Reproducibility

Fix random seeds (`random_state=…`), pin library versions, record the data file and its checksum, and save metrics with the model. AdmitFlow writes `lead_score.json` next to the model: version, training date, features, row counts, metrics.

## Check yourself

Train a `RandomForestClassifier` with the same features and split. Compare train and test AUC. Is it overfitting? Try `min_samples_leaf=20` and compare again.

Next: [Lesson 04 — Evaluating models honestly](04-evaluation.md)
