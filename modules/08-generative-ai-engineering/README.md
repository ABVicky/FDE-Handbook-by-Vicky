# Module 08 — Generative AI Engineering

> 💡 **In plain words:** This is the AI module most people come for. You'll build with large language models (LLMs, the technology behind tools like Claude and ChatGPT), and learn to make them answer from the client's own documents, correctly, with sources, and safely.
>
> 🛠️ **What you'll build:** AdmitFlow's AI assistant that answers students' questions about fees and courses, plus AI-written follow-up messages that a counsellor must approve before they're sent.
>
> ⏭️ **You can skip for now:** Lesson 04's vector-database details on a first pass. You don't need a paid AI account: everything works offline.
>
> 🧭 **Comes after:** [Module 07: AI and Machine Learning Fundamentals](../07-ai-and-machine-learning/README.md) · **Leads to:** [Module 09: Enterprise Systems and Integration](../09-enterprise-integration/README.md)
>
> 🪜 **How to work through it:** read the lessons in order → try the exercises → do the build → do the break & fix → do the Field Track → tick the "Done when" list. New here? Read [Start Here](../../START-HERE.md) first.

**Stage:** 3 — AI · **Time:** ~5 weeks at 15–20 h/week · **Builds:** C3 (Apply AI and data) · *Core specialization for AI FDE roles*
**Prerequisites:** [Module 07](../07-ai-and-machine-learning/README.md). An Anthropic API key (or another provider's) is optional; every required exercise and test runs offline.

## Outcome

After this module you can build, evaluate and ship LLM-powered features (retrieval-augmented answers, structured outputs, tool use and human-approved drafting) that are measurably reliable rather than just impressive in a demo, and you can explain their risks and costs to a client.

## Why this matters to an FDE

This is where Module 01's request, "an AI chatbot," finally gets built, and it gets built properly. Students ask the same questions at night; counsellors write the same follow-ups all day. A language model can help with both, as long as it never quotes last year's fees, never promises a job, never sends a message nobody approved, and has its quality measured on real questions.

## Checkpoint

Built and evaluated RAG systems before? Take the [checkpoint](checkpoint.md). Score ≥ 80% **and** complete the [build](build.md) and [break & fix](break-and-fix/README.md) to move on.

## Lessons

| # | Lesson | Core / Stretch | Time |
| --- | --- | --- | --- |
| 01 | [How large language models work (for builders)](lessons/01-how-llms-work.md) | Core | 3 h |
| 02 | [Calling LLM APIs well](lessons/02-calling-llm-apis.md) | Core | 5 h |
| 03 | [Retrieval-augmented generation](lessons/03-rag.md) | Core | 6 h |
| 04 | [Embeddings and vector search](lessons/04-embeddings-and-vector-search.md) | Core | 4 h |
| 05 | [Tool use, workflows and agents](lessons/05-tools-and-agents.md) | Core | 5 h |
| 06 | [Evaluating LLM features](lessons/06-evaluation.md) | Core | 5 h |
| 07 | [Security for LLM applications](lessons/07-llm-security.md) | Core | 3 h |
| 08 | [LLM features in production](lessons/08-production.md) | Core | 3 h |

## Practice

[exercises/](exercises/README.md): extend the evaluation set, hybrid search with rank fusion, a tool-use loop tested offline, and structured extraction from emails.

## Build: AdmitFlow's course assistant and follow-up drafter

See [build.md](build.md).

- **Data:** [`data/course_docs/`](../../projects/admitflow/data/course_docs/fees-2026.md) (7 documents, including a superseded fee schedule) and a 52-case [evaluation set](../../projects/admitflow/data/eval/assistant_eval.jsonl)
- **Goal:** a grounded, cited, evaluated assistant; drafts that can't be sent without approval
- **Reference solution:** [`rag.py`](../../projects/admitflow/admitflow/rag.py), [`llm.py`](../../projects/admitflow/admitflow/llm.py), [`assistant.py`](../../projects/admitflow/admitflow/assistant.py), [`evals.py`](../../projects/admitflow/admitflow/evals.py), [ADR-005](../../projects/admitflow/docs/adr/005-course-assistant.md)

## Break & fix

[break-and-fix/](break-and-fix/README.md): a demo assistant tells a parent last year's fee. Find every cause; fix it without deleting the old document.

## Field Track

See [field-track.md](field-track.md). Demo the assistant to the director, including where it fails, and agree acceptance criteria.

## Done when

- [ ] `admitflow eval-assistant` reports correct ≥ 0.85, retrieval@3 = 1.0, correct declines = 1.0, fees 13/13, enforced in CI
- [ ] Answers always cite retrieved sections; invented citations become "I don't know" (tested with a fake client)
- [ ] Superseded documents are never used for current answers
- [ ] Drafts are stored as `pending_approval`; only a permitted person can approve; an injected note can't cause sending (tested)
- [ ] The public endpoint works without login and limits input size
- [ ] Evaluation report written for the engine you'd ship
- [ ] [`progress/self-assessment.md`](../../progress/self-assessment.md) updated

## Resources

See [resources.md](resources.md).

---
*Last verified: 2026-11-21 · Model: `claude-opus-5-5` · Anthropic Python SDK 2.12 (Python 3.10+; request shape verified against a local stand-in server, not the live API). The offline engine and all tests run on Python 3.9+ with no API key.*
