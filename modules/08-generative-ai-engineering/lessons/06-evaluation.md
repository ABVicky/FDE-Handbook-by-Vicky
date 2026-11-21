# Lesson 06 — Evaluating LLM features

**Time:** ~5 hours · **Core** · *The most important lesson in this module*

## Why evaluation is the job

Demos are easy. Knowing whether a change made things better or worse (a new prompt, model, chunking rule or document) is what separates a prototype from a product. Without an evaluation set, every change is a guess, and every client conversation about quality is opinion against opinion.

## Build the test set before tuning

AdmitFlow's set: [`data/eval/assistant_eval.jsonl`](../../../projects/admitflow/data/eval/assistant_eval.jsonl), 52 cases.

```json
{"id": "Q01", "question": "How much is the Data Analytics course?",
 "expected_chunk": "fees-2026#diploma-fees", "also_acceptable": [],
 "must_include": ["1,800"], "must_not_include": [], "category": "fees"}
```

Where cases come from (best first):
1. **Real questions** from the client: emails, chat logs, counsellors' notes (anonymized)
2. **Stakeholders:** ask counsellors for the 20 questions they answer most
3. **Synthesized** cases (by you or a model), reviewed by a person

Cover the categories that matter: every topic, **questions the documents can't answer**, **prompt-injection attempts**, **outdated information**, different phrasings, typos, other languages if relevant.

## Metrics

| Metric | Measures | How |
| --- | --- | --- |
| **Retrieval@k** | Did the right section get retrieved? | Expected chunk in top k |
| **Correctness** | Is the answer right? | Required facts present, forbidden ones absent (deterministic) |
| **Groundedness** | Is every claim supported by a cited source? | Citations valid (code) + judge (below) |
| **Correct declines** | Does it say "I don't know" when it should? | Unanswerable cases |
| **Latency, cost** | p50/p95 seconds; cost per 1,000 questions | Timers, token usage |

Separate retrieval from generation: when a case fails, you need to know *which half* failed.

```bash
admitflow eval-assistant
```

```
correct 0.904 · retrieval@3 1.0 · declined_correctly 1.0 · fees 13/13
FAIL Q23 'What documents do I need to apply?': missing 'photo ID'
…
```

## Prefer deterministic checks

`must_include: ["1,800"]` is cheap, fast and unambiguous. Use it wherever a case has a factual core. Fee questions, dates, phone numbers and declines are all checked this way in AdmitFlow.

## LLM-as-judge, for what code can't check

For open-ended outputs ("is this follow-up draft polite, accurate and free of promises?"), a second model call can grade against a **rubric**:

```text
Grade the draft on each criterion (pass/fail, with a one-sentence reason):
1. Every fact appears in <course_info>.
2. No promise of admission, scholarship or job.
3. Under 120 words, with one clear next step.
4. Addresses the student by first name.
```

Rules for judges:
- **Validate the judge against people:** have counsellors grade 30–50 outputs too, and check agreement before trusting the judge.
- Specific, checkable criteria; pass/fail beats 1–10 scores.
- Use a capable model, and keep the judge prompt versioned and stable.
- Judges cost money per run. Keep deterministic checks in CI and run judged evaluations before releases.

## Evaluation in CI

AdmitFlow's test suite enforces a bar for the offline engine (`tests/test_assistant.py`): correct ≥ 0.85, retrieval@3 = 1.0, declines = 1.0, fees 13/13. Any change that breaks a fee answer fails the pull request.

For model-backed engines, run the evaluation **before switching** (`--llm claude`) and on a schedule (models and documents change). Record results with the model ID and the date in an [evaluation report](../../../templates/evaluation-report.md).

## Don't overfit the test set

While building AdmitFlow's assistant, it was tempting to keep adding synonyms until every case passed. That makes the number look good and the product no better. Countermeasures:
- Keep a **held-out** set you never look at while tuning
- Prefer fixes that generalize (better documents, better chunking) over case-specific hacks
- Keep adding **new real questions** after launch; the set should grow

## Check yourself

Do [Exercise 01](../exercises/01-extend-the-eval.md): add 15 new cases from realistic student questions (include 3 unanswerable and 2 injection attempts), run the evaluation, and classify each failure as retrieval, answer, data or test problem.

Next: [Lesson 07 — Security for LLM applications](07-llm-security.md)
