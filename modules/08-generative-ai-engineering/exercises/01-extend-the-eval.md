# Exercise 01 — Extend the evaluation set

1. Write **15 new cases** in the same JSON-lines format as [`assistant_eval.jsonl`](../../../projects/admitflow/data/eval/assistant_eval.jsonl): at least 3 unanswerable, 2 prompt-injection attempts, 2 with typos, and 2 phrased very differently from the documents.
2. Save them as `my-work/m08/extra_eval.jsonl` and run:
   ```bash
   admitflow eval-assistant --cases my-work/m08/extra_eval.jsonl
   ```
3. For each failure, classify the cause: **retrieval** (wrong section), **answer** (right section, wrong sentence or wording), **data** (the documents don't say it clearly), or **test** (your expectation was wrong).
4. Fix the two most important failures in a way that generalizes (better documents or chunking, not a synonym per case), and show the before/after numbers on **both** sets.
