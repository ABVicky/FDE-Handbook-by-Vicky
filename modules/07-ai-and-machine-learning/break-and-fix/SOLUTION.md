# Break & Fix — Solution

> ⚠️ Try it properly first.

## What's wrong

| # | Problem | Why it inflates the score |
| --- | --- | --- |
| 1 | **Target leakage:** `fee_paid`, `days_to_final_status` | Only known *after* the outcome. Paying the fee essentially **is** enrolling |
| 2 | **Leakage of actions:** `hours_to_first_contact`, `contacts_first_week` | Unknown when the lead arrives, and they're decisions the institute makes, not facts about the student |
| 3 | **Accuracy on imbalanced data** | 89% of leads don't enrol, so "always say no" already scores 89% |
| 4 | **Random split instead of a time split** | Mixing intakes lets the model learn intake-specific patterns (`intake` is even a feature!) and overstates future performance |
| 5 | **No baseline, no business metric** | Nothing to compare with; nothing about what counsellors would actually gain |

## The honest version

[`solution/honest_model.py`](solution/honest_model.py) drops the leaky columns, trains on 2024 and tests on 2025:

```
'Always predict not enrolled' accuracy: 89.3%
Honest model accuracy:                  89.3%
Honest model ROC AUC:                   0.581   (0.5 = random)
```

The honest model predicts "not enrolled" for everyone at the default threshold, so its accuracy equals the trivial baseline. Its ranking (AUC 0.58) is only somewhat better than random. AdmitFlow's own logistic model reaches 0.605, about the same as a simple source-rate baseline (0.609); see [ADR-004](../../../projects/admitflow/docs/adr/004-lead-scoring.md).

## Reply to the contractor

> Thanks for this. The pipeline is clean and easy to follow. Before we deploy, I re-ran it without the columns we only learn after a student's outcome (fee paid, days to final status) or that reflect our own follow-up (response time, contacts), and split by intake. Accuracy then equals the "always no" baseline. Could we look together at which enquiry-time signals might help, and agree on ranking metrics (AUC, precision in the top 20%) for the next version?

## Note to Ms. Rao

> The 99% figure came from information we only have after a student decides, so it can't predict new enquiries. Measured fairly, prediction from enquiry details is only slightly better than guessing by channel. What clearly matters is speed: leads called within a day enrol about six times as often as those left three days. I recommend we focus the pilot on response time, with the score as a small helper.

## Rules to remember

- For every feature: *is it known at prediction time?*
- Beat a trivial baseline **and** a simple baseline, on a split that mirrors real use.
- On imbalanced data, never report accuracy alone.
- "Too good to be true" usually is. Investigate before celebrating.
