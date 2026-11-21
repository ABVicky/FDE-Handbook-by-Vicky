# Lesson 04 — Evaluating models honestly

**Time:** ~4 hours · **Core**

## Why this matters

Evaluation is where models are oversold. A client who acts on an inflated number loses money and stops trusting you. An FDE's evaluation must be honest, compared with something simple, and translated into business terms.

## Always start with baselines

| Baseline | AdmitFlow result (2025 test intake) |
| --- | --- |
| **Trivial:** always predict the majority class | 89.3% accuracy ("never enrols") |
| **Simple:** a rule a spreadsheet user would build | Source conversion rate: AUC 0.609 |

A model that doesn't clearly beat the simple baseline isn't worth its complexity.

## The confusion matrix

At a chosen threshold (say, "call first if score > 0.15"):

| | Predicted enrol | Predicted not |
| --- | --- | --- |
| **Actually enrolled** | True positive (TP) | False negative (FN): a future student called late |
| **Didn't enrol** | False positive (FP): an early call that didn't convert | True negative (TN) |

- **Precision** = TP / (TP + FP): of those we prioritized, how many enrolled?
- **Recall** = TP / (TP + FN): of everyone who enrolled, how many did we prioritize?
- They trade off: a lower threshold raises recall and lowers precision.

## Metrics for ranking and probabilities

| Metric | Question it answers | AdmitFlow model |
| --- | --- | --- |
| **ROC AUC** | If I pick one enroller and one non-enroller, how often does the model rank the enroller higher? (0.5 = random, 1.0 = perfect) | 0.605 |
| **Precision@20%** | Of the top 20% by score, how many enrolled? Compare with the base rate | 15.7% (base 10.7%) |
| **Brier score** | Average squared error of the probabilities (lower = better; rewards calibration) | 0.0942 |
| **Calibration** | When the model says 20%, do ~20% enrol? | Check with `sklearn.calibration.calibration_curve` |

## Metrics that match the decision

Ask how the output will be **used**. Counsellors can make about 60 first calls a day while ~90 leads arrive on peak days. The real question is *"if we call in score order, how many more future students do we reach on day one?"*

[Exercise 03](../exercises/03-capacity.md) answers it: calling by score reaches **123** future students on day one, against **107** in random order, out of 160 on the 2025 intake. That's a real but modest gain, and much smaller than the effect of response time itself (16% vs 2.5% enrolment).

## Error analysis

Look at examples, not just averages:
- Which high-scoring leads didn't enrol? Which low scorers did?
- Does performance differ by course, source or campus? (Fairness and robustness: Lesson 07)
- Are there data-quality problems behind the errors (like the walk-in midnight timestamps)?

## Uncertainty

On 1,500 test leads with ~160 enrolments, AUC has a margin of several hundredths. **0.605 vs 0.609 is a tie.** Say so. Bootstrap the test set (resample with replacement, recompute, look at the spread) if a decision hinges on a small difference.

## Presenting results to a client

> *"Using only what we know when an enquiry arrives, the model ranks leads only slightly better than ordering by channel. Calling in score order would reach about 15% more future students on the first day than random order. The far bigger factor is speed: students called within a day enrol about six times as often as those left three days or more."*

Numbers, a comparison, a business translation and the caveat, in four sentences.

## Check yourself

Run the [break & fix](../break-and-fix/README.md) and write the note to Ms. Rao.

Next: [Lesson 05 — Serving and maintaining models](05-serving-models.md)
