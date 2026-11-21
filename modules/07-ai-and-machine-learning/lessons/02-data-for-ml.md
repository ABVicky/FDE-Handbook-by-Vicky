# Lesson 02 — Data for machine learning: features, labels, splits and leakage

**Time:** ~4 hours · **Core**

## The setup

A supervised dataset is a table: one row per example, **features** (inputs) and a **label** (the answer). AdmitFlow's history: [`data/historical_leads.csv`](../../../projects/admitflow/data/historical_leads.csv), 3,000 synthetic leads from the 2024 and 2025 intakes.

| Column | Role | Known when the lead arrives? |
| --- | --- | --- |
| `primary_source`, `course`, `n_channels`, `has_email`, `has_phone`, `received_at` | Candidate features | ✅ Yes |
| `hours_to_first_contact`, `contacts_first_week` | What *we* did afterwards | ❌ No |
| `fee_paid`, `days_to_final_status` | Consequences of the outcome | ❌ No |
| `enrolled` | **Label** | (the thing to predict) |

## Explore first

```python
import pandas as pd
df = pd.read_csv("data/historical_leads.csv", parse_dates=["received_at"])
df.shape, df.dtypes, df.isna().sum()
df["enrolled"].mean()                                  # base rate ≈ 0.12
df.groupby("primary_source")["enrolled"].agg(["count", "mean"])
```

Always find the **base rate** first. With 12% positives, "always no" is 88% accurate, which is why accuracy alone misleads (Lesson 04).

## Feature engineering

Turn raw columns into things a model can use:
- **Categories → one-hot columns:** `primary_source=walk-in` becomes a 0/1 column
- **Timestamps → meaningful parts:** hour, weekday, `out_of_hours`
- **Counts → relative values:** `extra_channels = n_channels − 1` (zero for the normal case, so the model's explanation reads correctly)
- **Missing values:** decide deliberately (a "missing" category, a default, or drop)

**Watch the data's quirks.** While building AdmitFlow's scorer, walk-in forms (date only, no time) all looked like they arrived at midnight, and so "out of hours." The fix: treat date-only walk-ins as in-hours. Feature bugs like this are invisible unless you check examples by hand.

## Leakage: the most common way to fool yourself

**Leakage** is using information during training that won't be available when the model is used. Symptoms: suspiciously high scores, and "important" features that look like the answer.

| Type | Example |
| --- | --- |
| **Target leakage** | `fee_paid`: paying the fee *is* enrolling |
| **Temporal leakage** | `hours_to_first_contact`: unknown when the lead arrives |
| **Train/test contamination** | Normalizing with statistics from the whole dataset, or the same student appearing in both sets |

The test for every feature: **"At the moment we make the prediction, do we know this value?"** The break & fix model scores 99.3% purely from leakage.

## Splitting: train, validation, test

- **Train set:** fit the model.
- **Validation set:** compare options and tune settings.
- **Test set:** final, untouched estimate. Look at it once.

**Split the way the model will be used.** AdmitFlow predicts *future* leads from *past* ones, so train on 2024 and test on 2025 (a **temporal split**). A random shuffle mixes the years and overstates performance. Notice the 2025 base rate (10.7%) differs from 2024 (13.1%): the world changes, and a temporal split shows you that.

## How much data?

More helps, but **positives** matter most. 1,500 leads at 13% gives ~200 enrolments to learn from. That's enough for a simple model with a handful of features, not for a complex one with hundreds.

## Check yourself

Do [Exercise 01](../exercises/01-explore.md). Then classify every column in `historical_leads.csv` as *feature*, *leakage* or *label*, with one sentence of justification each.

Next: [Lesson 03 — Training models with scikit-learn](03-training-models.md)
