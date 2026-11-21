# Lesson 05 — Serving and maintaining models

**Time:** ~3 hours · **Core**

## From notebook to product

A model only helps when it's inside the workflow: counsellors see a score where they already work. That means saving it, loading it in the API, versioning it, and watching it over time.

## Save with metadata

```python
import joblib
joblib.dump(pipeline, "models/lead_score.joblib")
```

AdmitFlow also writes `models/lead_score.json`:

```json
{"version": "lead-score-1", "trained_at": "…", "features": ["primary_source", "course", "…"],
 "train_rows": 1500, "test_rows": 1500,
 "metrics": {"baseline": {"roc_auc": 0.609, "…": "…"}, "model": {"roc_auc": 0.605, "…": "…"}}}
```

Every score the API returns includes `model_version`, so you can always tell which model produced it.

⚠️ `joblib`/pickle files can execute code when loaded. Only load model files you produced or trust, and load them with the same library versions used to save them.

## Serve through the API

```python
# admitflow/api/__init__.py — loaded once at startup, optional
app.state.scorer = load_scorer(os.environ.get("ADMITFLOW_MODEL", "models/lead_score.joblib"))
```

Endpoints ([`routes.py`](../../../projects/admitflow/admitflow/api/routes.py)):

| Endpoint | Returns |
| --- | --- |
| `GET /leads/{id}/score` | Probability, band (high/medium/low), top 3 reasons, model version |
| `GET /leads/priority?limit=20` | New leads to call next: waiting > 24h first, then by score |

If no model is loaded, both return `503 Lead scoring model not available`, and the rest of AdmitFlow keeps working. **An optional ML feature must never take down the core system.**

```json
{"lead_id": "WALKIN-0002", "probability": 0.193, "band": "high",
 "factors": ["+ came via walk-in", "+ course: Business Administration", "+ gave an email address"],
 "model_version": "lead-score-1"}
```

Counsellors see the **band and the reasons**, not "0.193": three decimal places imply a precision the model doesn't have.

## Batch or real-time?

| | Real-time (per request) | Batch (scheduled) |
| --- | --- | --- |
| When | Score when someone asks | Score all new leads nightly, store the result |
| Good for | Small, fast models (AdmitFlow) | Heavy models; reports |

## Monitoring: models decay

The world changes: new ad campaigns, a new course, a different intake. Watch:
- **Data drift:** input distributions change (suddenly 60% of leads from WhatsApp)
- **Performance:** once outcomes are known (end of intake), recompute AUC and precision@20% against the baseline
- **Usage:** do counsellors actually use the priority list?

Plan retraining **per intake**, through the same evaluation, and keep the old version until the new one is proven. If the model stops beating the baseline, retire it. That's a success of honest monitoring, not a failure.

## Check yourself

Train the model, start the API with `ADMITFLOW_MODEL` set, and call `/leads/priority` with a counsellor's token. Then stop the API, delete the model file, start it again, and confirm everything except scoring still works.

Next: [Lesson 06 — Neural networks, transformers and embeddings](06-neural-networks-and-embeddings.md)
