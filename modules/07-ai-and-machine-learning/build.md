# Module 07 Build — Lead scoring, honestly

**Time:** ~15–20 hours · **Capabilities:** C3

## Scenario

The admissions office has dug out two past intakes with outcomes: [`historical_leads.csv`](../../projects/admitflow/data/historical_leads.csv) (3,000 leads, synthetic). Ms. Rao: *"Now we have data. Can AI tell counsellors who will enrol, so they call those students first?"*

## Requirements

1. **Frame it:** a one-paragraph problem framing: prediction target, when the prediction is made, who uses it, and what decision it changes.
2. **Data:** classify every column as feature / leakage / label; a test that fails if a leaky column is ever used.
3. **Train and evaluate:** temporal split (train 2024, test 2025); a simple baseline; report ROC AUC, precision@20%, Brier score and base rate. Fix the walk-in date-only issue (or find your own data quirks).
4. **Serve:** `admitflow train-model` saves the model and metadata; the API exposes `GET /leads/{id}/score` (band, reasons, model version) and `GET /leads/priority` (waiting > 24h first, then score). Without a model: `503` for scoring, everything else unaffected.
5. **Analyse the lever:** enrolment rate by time to first contact, with the caveat that it's correlation.
6. **Decide and document:** an ADR on whether and how to use the score, and a model card.
7. **Tests:** leakage, metrics vs baseline, explanations, API endpoints, missing-model behaviour.

## Running the reference solution

```bash
cd projects/admitflow
```

```bash
python -m pip install -e ".[api,db,ml,dev]"
```

```bash
admitflow train-model data/historical_leads.csv --out models/lead_score.joblib
```

```bash
ADMITFLOW_MODEL=models/lead_score.joblib admitflow serve
```

Then (with a token from `/auth/login`) call `GET /leads/priority`.

## Expected results

```
            ROC AUC  prec@20%   Brier
baseline      0.609     0.143  0.0949
model         0.605     0.157  0.0942
```

Yes, the model and the baseline are effectively tied. **That's the expected result**, and your write-up should say so plainly, then point to the response-time finding.

## Done when

- [ ] Leakage test in place; no leaky features used
- [ ] Metrics reported against the baseline on the 2025 intake
- [ ] Scoring endpoints work; app works with no model
- [ ] ADR and model card written
- [ ] Recommendation to the client written (see the Field Track)

## Stretch

- Calibrate the model (`CalibratedClassifierCV`) and plot a calibration curve
- Bootstrap confidence intervals for AUC
- Add a "priority" panel to the React dashboard using `/leads/priority`
