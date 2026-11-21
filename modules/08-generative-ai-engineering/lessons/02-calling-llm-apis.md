# Lesson 02 — Calling LLM APIs well

**Time:** ~5 hours · **Core**

Examples use the official Anthropic Python SDK (`anthropic`, version 2.x, which needs Python 3.10+). Other providers' SDKs follow similar shapes; AdmitFlow keeps provider code behind small interfaces (`Answerer`, `Drafter`) so it can be swapped.

```bash
python -m pip install anthropic
```

Credentials come from the environment (`ANTHROPIC_API_KEY`) or from `ant auth login`. **Never** put a key in code, a frontend, or a Git repository.

## A basic call

```python
import anthropic

client = anthropic.Anthropic()          # reads credentials from the environment

response = client.messages.create(
    model="claude-opus-5-5",
    max_tokens=16000,
    system="You help prospective students of Northbridge Institute. Be brief and friendly.",
    messages=[{"role": "user", "content": "What courses do you offer in the evening?"}],
)

if response.stop_reason == "refusal":
    print("The model declined.")
else:
    for block in response.content:       # a list of blocks: text, thinking, tool_use…
        if block.type == "text":
            print(block.text)
```

The API is **stateless**: for a conversation, send the whole history each time (`messages` alternates `user` / `assistant`).

## Structured outputs: JSON you can trust

When code consumes the answer, ask for a schema instead of parsing prose. AdmitFlow's answerer ([`llm.py`](../../../projects/admitflow/admitflow/llm.py)):

```python
from typing import List
from pydantic import BaseModel

class GroundedAnswer(BaseModel):
    answerable: bool
    answer: str
    citations: List[str]

response = client.beta.messages.parse(
    model="claude-opus-5-5",
    max_tokens=8000,
    system=ANSWER_SYSTEM,
    output_config={"effort": "low"},
    betas=["server-side-fallback-2026-07-01"],
    fallbacks="default",
    messages=[{"role": "user", "content": f"{documents}\n\n<question>{question}</question>"}],
    output_format=GroundedAnswer,
)
result = response.parsed_output        # a validated GroundedAnswer (or None if the model refused)
```

What each setting is for:
- **`output_format`**: the reply must match the schema; the SDK validates it into a Pydantic object.
- **`output_config={"effort": "low"}`**: short factual answers don't need much reasoning; lower effort is faster and cheaper. Measure quality on your evaluation set before lowering it for harder tasks.
- **`fallbacks="default"`** (with its beta flag): if the model declines a request for safety reasons, the API automatically retries it on a fallback model within the same call. Your code must still check `stop_reason == "refusal"`, because the whole chain can decline.

The handbook verified this exact request against SDK 2.12 with a local stand-in server: it sends the `anthropic-beta: server-side-fallback-2026-07-01` header, `fallbacks: "default"`, `effort: "low"` and a `json_schema` output format.

## Streaming

For chat interfaces, show text as it arrives:

```python
with client.messages.stream(
    model="claude-opus-5-5",
    max_tokens=64000,
    messages=[{"role": "user", "content": question}],
) as stream:
    for text in stream.text_stream:
        print(text, end="", flush=True)
    final = stream.get_final_message()   # the complete message, with usage and stop_reason
```

Use streaming whenever replies may be long. It also avoids request timeouts on long generations.

## Errors and retries

The SDK retries connection errors, 429 (rate limited) and 5xx responses automatically (2 retries by default). Handle what's left specifically, most specific first:

```python
try:
    response = client.messages.create(...)
except anthropic.RateLimitError:
    ...   # back off; show "busy, try again"
except anthropic.APIStatusError as error:
    if error.status_code >= 500:
        ...   # provider problem: fall back to the offline answerer
    else:
        raise  # 400s are our bug: log and fix
except anthropic.APIConnectionError:
    ...   # network: fall back
```

**Design for the provider being down.** AdmitFlow falls back to its offline engine; a draft request falls back to the template. The core system must keep working without the model.

## Prompt structure that works

- **System prompt:** role, audience, rules, output expectations. Keep it stable (it can be cached; Lesson 08).
- **Data in tags:** wrap retrieved documents, user questions and records in clear tags (`<documents>`, `<question>`, `<lead_record>`), and say that tag contents are data, not instructions (Lesson 07).
- **Be specific about failure:** "If the documents don't contain the answer, set answerable=false" works better than "don't make things up."
- **Version prompts in Git** next to the code, and re-run the evaluation whenever they change.

## Model choice in code

Keep the model ID in one place (`MODEL = "claude-opus-5-5"` in `llm.py`), and record it with every output (AdmitFlow stores `engine` on drafts). When a new model comes out, change one line, then run the evaluation.

## Check yourself

Write a function `classify_enquiry(text) -> {"course": str | None, "wants_callback": bool, "language": str}` using structured outputs. Then write three unit tests that use a fake client (see `FakeClient` in [`tests/test_assistant.py`](../../../projects/admitflow/tests/test_assistant.py)) so they run without network or cost.

Next: [Lesson 03 — Retrieval-augmented generation](03-rag.md)
