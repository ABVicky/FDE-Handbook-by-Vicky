# Module 07 — AI and Machine Learning Fundamentals

> 💡 **In plain words:** Before building with AI, you need to understand it, and to be honest about when it helps. You'll train a simple prediction model and learn the most common way people fool themselves with AI.
>
> 🛠️ **What you'll build:** A model that predicts which enquiries are likely to enrol. You'll also discover something more useful: replying quickly matters far more than any prediction.
>
> ⏭️ **You can skip for now:** Lesson 06's deeper topics (neural networks, PyTorch) beyond the main ideas.
>
> 🧭 **Comes after:** [Module 06: Cloud and Infrastructure](../06-cloud-and-infrastructure/README.md) · **Leads to:** [Module 08: Generative AI Engineering](../08-generative-ai-engineering/README.md)
>
> 🪜 **How to work through it:** read the lessons in order → try the exercises → do the build → do the break & fix → do the Field Track → tick the "Done when" list. New here? Read [Start Here](../../START-HERE.md) first.

**Stage:** 3 — AI · **Time:** ~3 weeks at 15–20 h/week · **Builds:** C3 (Apply AI and data)
**Prerequisites:** [Module 05](../05-databases-and-data-engineering/README.md) (data) and [Module 06](../06-cloud-and-infrastructure/README.md) (deployment). No maths beyond school level.

## Outcome

After this module you can frame a prediction problem, prepare data without leakage, train and evaluate models against baselines, serve a model safely inside an application, and explain its value and limits honestly to a client.

## Why this matters to an FDE

Ms. Rao's original request was "AI." With two years of outcomes now in hand, you can finally test what prediction can do for the institute. The honest answer turns out to be: **a little**. And the data points to something much more valuable: **response speed**. An FDE who can show that clearly, with evidence, earns more trust than one who ships an impressive-looking model.

## Checkpoint

Comfortable with scikit-learn, leakage and evaluation? Take the [checkpoint](checkpoint.md). Score ≥ 80% **and** complete the [build](build.md) and [break & fix](break-and-fix/README.md) to move on.

## Lessons

| # | Lesson | Core / Stretch | Time |
| --- | --- | --- | --- |
| 01 | [What AI and ML are (and when not to use them)](lessons/01-what-ai-and-ml-are.md) | Core | 2 h |
| 02 | [Data for ML: features, labels, splits and leakage](lessons/02-data-for-ml.md) | Core | 4 h |
| 03 | [Training models with scikit-learn](lessons/03-training-models.md) | Core | 5 h |
| 04 | [Evaluating models honestly](lessons/04-evaluation.md) | Core | 4 h |
| 05 | [Serving and maintaining models](lessons/05-serving-models.md) | Core | 3 h |
| 06 | [Neural networks, transformers and embeddings](lessons/06-neural-networks-and-embeddings.md) | Core / Stretch | 3 h |
| 07 | [Responsible ML: bias, explanations and oversight](lessons/07-responsible-ml.md) | Core | 2 h |

## Practice

[exercises/](exercises/README.md): explore the history, compare models honestly, turn scores into a capacity decision, and a first taste of text similarity.

## Build: lead scoring, honestly

See [build.md](build.md).

- **Data:** [`historical_leads.csv`](../../projects/admitflow/data/historical_leads.csv): 3,000 synthetic leads from two intakes, with outcomes
- **Goal:** a leakage-free, baseline-compared model served through the API with explanations, plus a recommendation the client can act on
- **Reference solution:** [`admitflow/scoring.py`](../../projects/admitflow/admitflow/scoring.py), [`tests/test_scoring.py`](../../projects/admitflow/tests/test_scoring.py), [ADR-004](../../projects/admitflow/docs/adr/004-lead-scoring.md)

## Break & fix

[break-and-fix/](break-and-fix/README.md): a contractor's "99% accurate" model. Find out why it's worthless.

## Field Track

See [field-track.md](field-track.md). Explain the model's real value, and the response-time finding, to the director.

## Done when

- [ ] Every feature passes the "known at prediction time?" test, and a test enforces it
- [ ] Model and simple baseline compared on a temporal split, with AUC, precision@20% and the base rate
- [ ] Scores served through the API with bands and reasons; the app works without the model
- [ ] Capacity analysis done; model card written
- [ ] Break & fix reply and note written
- [ ] Director one-pager tested on a non-technical reader
- [ ] [`progress/self-assessment.md`](../../progress/self-assessment.md) updated

## Resources

See [resources.md](resources.md).

---
*Last verified: 2026-11-21 · Tested with: scikit-learn 1.6, pandas 2.3, Python 3.9+. (On some macOS builds, numpy prints harmless "divide by zero in matmul" warnings during training; results are unaffected.)*
