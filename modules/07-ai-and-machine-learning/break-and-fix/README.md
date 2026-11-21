# Module 07 — Break & Fix: The 99% model

**Time:** 1–2 hours · Do this after [Lesson 04](../lessons/04-evaluation.md).

## The situation

A contractor delivered a lead-scoring model with a one-line summary: **"99% accurate. Ready for production."** Ms. Rao is excited and wants it live next week. Before anyone uses it, you've been asked to review it.

```bash
cd modules/07-ai-and-machine-learning/break-and-fix
```

```bash
python amazing_model.py
```

```
Accuracy: 99.3%
Most important features: fee_paid, days_to_final_status, hours_to_first_contact, contacts_first_week, intake
```

## Your job

1. Find **every** reason this number can't be trusted. There are at least four.
2. Write an honest version: what does a correct evaluation show?
3. Compare it with the simplest possible "model": always predicting *not enrolled*.
4. Write a short, respectful reply to the contractor and a 4-line note to Ms. Rao explaining what the model can and can't do.

## Hints

<details><summary>Hint 1</summary>For each important feature, ask: <em>at the moment a new enquiry arrives, do we know this value?</em></details>

<details><summary>Hint 2</summary>About 11% of leads enrol. What accuracy do you get by never predicting enrolment?</details>

<details><summary>Hint 3</summary><code>train_test_split</code> shuffles 2024 and 2025 together. How will the model actually be used?</details>

When you're done: [SOLUTION.md](SOLUTION.md)
