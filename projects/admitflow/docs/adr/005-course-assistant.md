# ADR-005: A grounded course assistant as a workflow, with human-approved drafts

**Status:** Accepted · **Date:** Module 08

## Context
Ms. Rao's original request (Module 01) was "an AI chatbot." By now the real needs are clear: (1) prospective students ask the same ~20 questions, often at night; (2) counsellors spend time writing similar follow-up messages. Wrong answers about fees or promises about jobs carry real risk (complaints, data-protection and consumer issues). The institute is budget-conscious and has little IT capacity.

## Decision
- **Retrieval-augmented answers** from the institute's own documents only (`data/course_docs`), chunked by section with metadata; superseded documents excluded; BM25 retrieval (top 3).
- **Grounding enforced in code:** answers must cite retrieved sections; invented or missing citations become "I don't know" with the admissions phone number.
- **Two engines behind one interface:** an offline extractive engine (default: free, deterministic, used in CI) and Claude (`ADMITFLOW_LLM=claude`, `claude-opus-5-5`, low effort, structured outputs, server-side refusal fallbacks).
- **Follow-up drafting is a fixed workflow, not an autonomous agent:** retrieve → draft → store as `pending_approval`. The model has no tool that sends anything; a counsellor approves the exact text (Module 09 sends approved drafts).
- **Evaluation gates changes:** 52 cases; CI requires correct ≥ 0.85, retrieval@3 = 1.0, correct declines = 1.0 and fees 13/13 for the offline engine.

## Consequences
- ✅ The riskiest failure (wrong or outdated fees, invented promises) is controlled structurally, not by prompt wording alone.
- ✅ Works without any API key; Claude is an upgrade, not a dependency.
- ⚠️ The offline engine misses paraphrases; an FAQ document written from real questions closes the biggest gaps. Claude's answers must be evaluated on the same set before being switched on (`admitflow eval-assistant --llm claude`, which costs money per run).
- ⚠️ The public endpoint needs rate limiting and abuse monitoring (Module 10).
- ➡️ Revisit embeddings / hybrid search if the document set grows past a few hundred sections, or students ask in other languages.

## Alternatives considered
- **Off-the-shelf chatbot builder:** fast to demo, but no control over grounding, citations or data location.
- **Autonomous agent with a "send message" tool:** rejected. One injected instruction in a lead's note could cause messages to be sent. Approval must be structural.
- **Fine-tuning a model on the documents:** unnecessary for ~25 sections that change every year; RAG updates when a document changes.
