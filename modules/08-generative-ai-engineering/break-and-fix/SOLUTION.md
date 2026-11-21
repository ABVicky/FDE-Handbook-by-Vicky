# Break & Fix — Solution

> ⚠️ Try it properly first.

## Root causes

| # | Cause | Effect |
| --- | --- | --- |
| 1 | **Metadata thrown away.** `superseded: true` and `effective_from` are read as plain text, never used | The 2025 schedule competes equally with 2026 |
| 2 | **Fixed-size chunks** (every 400 characters) | The 2026 fee table is split across chunks, so its "Data Analytics" row loses its "Fee per term" header and context; the 2025 table happens to fit in one chunk and wins |
| 3 | **Top-1 retrieval by raw word overlap** | No ranking by term importance, no second chance, no notion of "this doesn't really match" |
| 4 | **No answer step, no citation, no "I don't know"** | The user sees a raw chunk with no date or source, so nobody could spot that it's last year's |
| 5 | **No evaluation** | Nothing tested fee questions after the 2026 schedule was added |

Deleting the old file would hide causes 2–5 and break finance's records. The fix belongs in the pipeline.

## The fix (AdmitFlow's assistant)

- **Section-based chunks with metadata** ([`rag.py`](../../../projects/admitflow/admitflow/rag.py) `chunk_document`): one chunk per `##` section, with document title, section name, `effective_from` and `superseded`.
- **Filter before ranking:** `Retriever.search` excludes superseded documents by default, and accepts `as_of=` for questions about a specific date.
- **BM25 ranking, top 3**, with a light stemmer and query expansion ("how much" → "fee").
- **Grounded answers:** every answer cites its section ("Source: Fee schedule 2026–27, Diploma fees"); weak matches become "I don't know".
- **Evaluation:** 13 fee cases in [`assistant_eval.jsonl`](../../../projects/admitflow/data/eval/assistant_eval.jsonl), including "What was the Data Analytics fee last year?" with `must_not_include: ["1,650"]`. CI fails if fees aren't 13/13.

Regression check: [`solution/check_fees.py`](solution/check_fees.py) asks every course's fee three ways:

```
18/18 fee answers correct
```

## Reply to the parent

> Thank you for telling us, and we're sorry for the confusion. The correct Data Analytics fee for the 2026 intake is 1,800 per term, as on your invoice. Our chat assistant showed last year's fee by mistake; we've fixed it so it only uses the current fee schedule. If you'd like to discuss instalments or scholarships, a counsellor will call you today.

## Incident note

> The website assistant showed 2025 fees because it ignored which documents were out of date. Fixed by filtering superseded documents and citing sources in every answer. An automated check now runs 18 fee questions on every change. We're contacting students who used the chat in the last month about fees.

## The general lesson

RAG failures are usually **data and retrieval** failures, not model failures. Keep metadata, chunk by meaning, filter by validity, cite sources, and test with real questions, before you think about prompts or bigger models.
