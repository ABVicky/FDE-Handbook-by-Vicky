# Lesson 08 — LLM features in production: cost, latency, monitoring, change

**Time:** ~3 hours · **Core**

## Cost

Cost per request ≈ input tokens × input price + output tokens × output price. Estimate per *completed task* (an answered question, an approved draft), including retries and fallbacks.

Levers, cheapest first:
1. **Send less:** top 3 sections, not the whole document set; short system prompts; trimmed history.
2. **Prompt caching:** a stable prefix (system prompt, tool definitions) can be cached by the provider so repeated requests pay much less for it. Keep the cached part byte-for-byte identical: no timestamps or user names in it.
3. **Lower effort** for simple tasks (AdmitFlow uses `low` for FAQ answers and drafts).
4. **Batch processing** for non-urgent work (e.g. drafting 300 follow-ups overnight): providers offer batch APIs at a discount.
5. **A smaller model** for a sub-task, *only if the evaluation shows quality holds*.

Before changing anything, measure the baseline on the evaluation set. After each change, measure again. A cheaper setup that fails more often isn't cheaper.

## Latency

Users wait for: retrieval + time to first token + generation. Stream the answer (Lesson 02), keep prompts short, and keep retrieval fast (BM25 over 25 sections takes microseconds). Set **timeouts** and fall back to the offline answer or "a counsellor will reply" instead of spinning forever.

## Observability

Log, for every model call: request ID, model, engine, input/output tokens, latency, stop reason, whether it answered, and citations. **Not** full prompts with personal data, by default. AdmitFlow logs `assistant answered=… citations=… engine=…` on every question.

Watch:
- decline rate (a jump may mean a broken document or index)
- refusal and fallback rate
- cost per day against budget
- user feedback (a thumbs-down button is cheap and valuable)

Module 10 adds tracing across API → retrieval → model.

## Change management

Things that change under you:
- **Documents:** new fee schedule each year. The pipeline must handle supersession (break & fix).
- **Models:** providers release new models and retire old ones. Pin the model ID, re-run the evaluation before upgrading, and read migration notes (API behaviour can change between versions).
- **SDKs:** major versions can change interfaces (this handbook found SDK 2.x installed where docs described 1.x). Pin versions, and run tests before upgrading.
- **Prompts:** versioned in Git; every change goes through the evaluation.

## Rollout

1. Offline engine live (free, safe baseline)
2. Model engine evaluated on the same set → [evaluation report](../../../templates/evaluation-report.md)
3. **Shadow mode:** run the model on real questions without showing its answers; compare
4. Limited rollout (e.g. counsellor-facing first, then public)
5. Monitor; keep the switch (`ADMITFLOW_LLM`) to fall back instantly

## Check yourself

Estimate monthly cost for AdmitFlow's public assistant at 3,000 questions a month, using the provider's current price list and your own token counts (`messages.count_tokens` on a realistic request). Then list the three levers you'd try first, and how you'd measure each.

Next: [Exercises](../exercises/README.md) and the [build](../build.md).
