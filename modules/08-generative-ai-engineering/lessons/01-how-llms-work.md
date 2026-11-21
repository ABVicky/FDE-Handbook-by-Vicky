# Lesson 01 — How large language models work (for builders)

**Time:** ~3 hours · **Core**

## Why this matters

You don't need to train a language model to deploy one well. But every design decision in this module (what to put in the prompt, how much context to send, how to stop it inventing fees, what it will cost) follows from a few facts about how these models behave.

## Tokens

Models read and write **tokens**: chunks of text, often a word or part of a word. "Northbridge" might be 2–3 tokens; a number like "1,800" a few more. Everything is measured in tokens: limits, speed and price.

- Non-English text, code and numbers often use more tokens per word.
- Count, don't guess: providers offer token-counting endpoints (Anthropic: `messages.count_tokens`).

## The context window

The **context window** is everything the model sees in one request: system prompt, conversation, retrieved documents, tool definitions, and its own reply. Current frontier models accept very large contexts (hundreds of thousands to a million tokens), but more context means more cost and latency, and important details can get diluted. **Send what's relevant, not everything you have.** That's the whole idea behind retrieval (Lesson 03).

## Next-token prediction, and why models "hallucinate"

A language model generates text one token at a time, choosing each token based on everything before it. It was trained to produce *plausible* text, then further trained to follow instructions and be helpful. It has no built-in notion of "I checked this."

So when the answer isn't in its context, it may produce a fluent, confident, **wrong** answer, such as last year's fee or a plausible-sounding job guarantee. Hallucination is not a bug you can patch out; it's managed by design:
- give the model the right facts in context (**retrieval**)
- require it to **cite** them, and check the citations in code
- let it (and make it) say **"I don't know"**
- **evaluate** against real questions (Lesson 06)

## Model families and choosing one

Providers offer families with trade-offs between capability, speed and price. Anthropic's current models (late 2026) include Claude Opus 5.5 (`claude-opus-5-5`, the general default), Claude Sonnet 5.5 (fast, lower cost), Claude Haiku 5.5 (fastest, cheapest) and Claude Fable 5.2 (most capable, highest price). OpenAI, Google and others have equivalents, and open-weight models (Llama, Mistral, Qwen and others) can run on your own infrastructure.

How to choose for a client:
1. **Start with a capable model** and get the feature working and evaluated.
2. **Then** optimize: lower effort settings, caching, smaller models for simple sub-tasks. Measure on your evaluation set at every step.
3. Consider **where data may go.** Some clients require a specific cloud (Claude is also available through AWS, Google Cloud and Microsoft Azure) or an open-weight model inside their network.

Model names and prices change every few months. Check the provider's current model list rather than trusting a blog post (or this lesson) from last year.

## Controls you'll use

| Control | What it does | AdmitFlow setting |
| --- | --- | --- |
| **System prompt** | Standing instructions and rules | Answer only from documents; cite; never promise jobs |
| **max_tokens** | Hard cap on the reply length | 8,000 (generous, so answers aren't cut off) |
| **Effort / thinking** | How much the model reasons before answering. Current Claude models use *adaptive thinking*, tuned with an effort level | `low`: short factual answers don't need deep reasoning |
| **Structured output** | Forces the reply into a JSON schema | `{answerable, answer, citations}` |
| **Stop reason** | Why the reply ended: finished, hit the token cap, wants a tool, or **refused** | Refusals become "I don't know" |

(Older material talks about `temperature` for randomness. Current Claude models don't accept sampling parameters; control behaviour with prompts, effort and structured outputs.)

## Cost and latency, roughly

Price is per million input and output tokens; output costs more. A FAQ answer with three retrieved sections is ~1,500 input tokens and ~100 output tokens. Multiply by questions per month and you have a budget line Ms. Chen can approve. Lesson 08 covers caching and other levers.

## Check yourself

1. Explain to Ms. Rao in three sentences why "just use ChatGPT for our website" could tell students the wrong fee, and what we do instead.
2. What would happen if AdmitFlow sent all 25 document sections with every question instead of the top 3? Name one benefit and two costs.

Next: [Lesson 02 — Calling LLM APIs well](02-calling-llm-apis.md)
