# Module 08 Build — AdmitFlow's course assistant and follow-up drafter

**Time:** ~30–35 hours · **Capabilities:** C3

## Scenario

Ms. Rao's original wish, "an AI chatbot," is now a reasonable next step: the data is clean, the team trusts AdmitFlow, and you know the real needs.
1. **Students** ask the same questions at night (fees, timings, campuses, jobs).
2. **Counsellors** write similar follow-up messages all day.

Ms. Chen's condition: *"If it ever tells a student the wrong fee, or sends something without a counsellor seeing it, we switch it off."*

## Requirements

### 1. Documents and retrieval
- Load [`data/course_docs`](../../projects/admitflow/data/course_docs/fees-2026.md); chunk by section with metadata (title, section, `effective_from`, `superseded`)
- Exclude superseded documents by default; support an `as_of` date
- Rank with BM25 (or better), top 3

### 2. Answering
- An **offline engine** that only uses document text and declines weak matches
- A **model engine** (Claude or another provider) with structured output `{answerable, answer, citations}`, documents and questions in tags, a "data, not instructions" rule, refusal handling, and fallback to the offline engine on errors
- **Citations verified in code**; invalid or missing → "I don't know" + contact details
- `POST /public/assistant/ask` (public, input ≤ 500 characters) and `admitflow ask`

### 3. Evaluation
- `admitflow eval-assistant` over the 52-case set, with retrieval@3, correctness, correct declines and per-category results; `--min-correct` for CI
- CI bar for the offline engine: correct ≥ 0.85, retrieval@3 = 1.0, declines = 1.0, fees 13/13
- An [evaluation report](../../templates/evaluation-report.md) for the engine you'd ship

### 4. Follow-up drafts with human approval
- `POST /leads/{id}/drafts` → a draft (`pending_approval`) from lead details, notes and relevant course sections
- `GET /drafts`, `POST /drafts/{id}/approve`, `POST /drafts/{id}/reject`, with the same assignment rules as leads; `409` if already decided
- Stored in both repositories (contract tests) with an Alembic migration
- **No code path that sends an unapproved draft**, with a test using an injected note

### 5. Decision record
An ADR covering the workflow-vs-agent decision, grounding, engines, and what would trigger embeddings.

## Running the reference solution

```bash
cd projects/admitflow
```

```bash
admitflow ask "How much is the Data Analytics course?"
```

```bash
admitflow eval-assistant --min-correct 0.85
```

With the API running (`admitflow serve`), `POST /public/assistant/ask` with `{"question": "Do you offer evening classes?"}`.

To try Claude (Python 3.10+, credentials set; **each evaluation run costs money**):

```bash
python -m pip install -e ".[llm]"
```

```bash
admitflow eval-assistant --llm claude
```

## Expected offline results

```
correct 0.904 · retrieval@3 1.0 · declined_correctly 1.0
fees 13/13 · courses 9/9 · placements 4/4 · injection 3/3 · outdated 1/1
```

The 5 offline failures are sentence-selection misses, which a model engine should fix. Prove it with the evaluation before switching.

## Done when

- [ ] Every requirement above, with tests
- [ ] Evaluation bar enforced in CI
- [ ] Evaluation report and ADR written
- [ ] Demo done (Field Track)

## Stretch

- Hybrid retrieval with a real embedding model (Exercise 02), measured
- Stream answers to a chat widget in the React dashboard
- A "was this helpful?" button that logs feedback for future evaluation cases
- An LLM-as-judge rubric for drafts, validated against counsellors' ratings
