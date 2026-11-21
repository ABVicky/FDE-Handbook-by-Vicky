# Lesson 07 — Responsible ML: bias, explanations and human oversight

**Time:** ~2 hours · **Core**

## Why this matters

A lead score changes who gets called first, and so, a little, who gets an education. Models can encode unfairness from history, and people over-trust numbers that look precise. Responsible ML isn't a separate discipline; it's a set of habits built into everything above.

## Where bias comes from

- **Historical data reflects past decisions.** If counsellors historically called ad leads last, ad leads enrolled less, and a model learns "ad leads are bad", reinforcing the pattern.
- **Proxies.** Even without sensitive attributes, other features can stand in for them. A name's script or spelling, a neighbourhood, or a phone prefix can correlate with ethnicity, religion or income.
- **Unequal error rates.** A model can be accurate overall but much worse for one group.

AdmitFlow deliberately **does not** use name, gender, age, address or anything derived from them. Check that rule in [`scoring.py`](../../../projects/admitflow/admitflow/scoring.py): `FEATURES` has six columns, all about the enquiry.

## Check for unequal impact

Compare metrics across groups you can legitimately measure (course, campus, source):

```python
for course, group in test.groupby("course"):
    print(course, roc_auc_score(group.enrolled, group.score), precision_at(group.score, group.enrolled))
```

Big differences need explaining before deployment, and a conversation with the client about whether they're acceptable.

## Explanations

People should be able to see **why** a score is what it is. For logistic regression, each feature's contribution is its weight × its value, which is what AdmitFlow shows as "+ came via walk-in", "− came via ad." For complex models, tools such as SHAP estimate contributions.

Explanations also catch bugs: the walk-in "out of hours" bug was spotted because an explanation looked wrong.

## Human oversight by design

| Principle | AdmitFlow implementation |
| --- | --- |
| The model **assists**, people **decide** | Score orders the queue; it never removes a lead from it |
| Speed first | Leads waiting > 24h jump ahead regardless of score |
| No false precision | Bands, not decimals |
| Labelled clearly | "Experimental" in the UI; model version in every response |
| Reversible | Can be switched off without affecting anything else (`503`, core keeps working) |
| Reviewed | Re-evaluated every intake; retired if it stops beating the baseline |

## Talking about it with clients

- Be clear about what the model **can't** do, before they ask.
- Put uncertainty in words: "slightly better than ordering by channel", not "AUC 0.605."
- Document intended use and limits in a short **model card**: purpose, data, features, metrics, limitations, owner, review date. (The `lead_score.json` metadata + [ADR-004](../../../projects/admitflow/docs/adr/004-lead-scoring.md) cover most of it.)
- Some uses carry legal obligations (automated decisions about people, in many jurisdictions). If a model would *decide* rather than *assist*, involve the client's legal and privacy team.

## Check yourself

Write a one-page **model card** for AdmitFlow's lead score: intended use, users, data, features (and excluded ones, with reasons), metrics vs baseline, known limitations, fairness checks done, owner, and next review date.

Next: [Exercises](../exercises/README.md) and the [build](../build.md).
