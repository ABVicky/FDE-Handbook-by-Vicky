# Lesson 04 — A week in the life

**Time:** ~1 hour · **Core**

This is an **illustrative** week, a composite of typical FDE work, not one person's diary. Real weeks vary by company, customer and project stage.

**Setting:** You're an FDE at an AI platform company. Your customer is a regional insurance company. The goal is to cut the time it takes claims handlers to review incoming claim documents. You're in week 3 of the engagement.

| Day | What happens | Skills used |
| --- | --- | --- |
| **Mon** | Morning stand-up with the customer's IT lead. You learn that the document store you planned to use is being migrated next month. You revise the integration plan and write an Architecture Decision Record (ADR) explaining the change. Afternoon: you build an extraction pipeline for claim PDFs. | Communication, adaptability, data engineering |
| **Tue** | You sit with two claims handlers for two hours and watch them work. You discover they don't read whole documents; they look for six specific fields. That changes the design: extract those six fields reliably instead of summarizing everything. | Discovery, observation, product thinking |
| **Wed** | Heads-down engineering. You build field extraction with an LLM and structured output, plus a test set of 80 real (anonymized) claims with hand-checked answers. First accuracy run: 74%. Most failures are scanned handwritten forms. | AI engineering, evaluation |
| **Thu** | The customer's security team reviews your design. They require that no claim data leaves their cloud region. You confirm the model deployment meets this and document data flows. In the afternoon you improve the handwritten-form handling; accuracy rises to 88%. | Security, compliance, iteration |
| **Fri** | Demo to the claims director. You show the 88%, *and* the 12% failures, and propose that low-confidence extractions go to a human. They agree on a target: 90% accuracy plus human review, measured over a two-week pilot. You write the weekly status update and send your product team a note: "Three customers now need handwritten-form support." | Presentation, expectation management, feedback to product |

## What to notice

1. **Code is maybe half the week.** The rest is understanding, deciding, documenting and communicating. None of it is "overhead"; it's what makes the code worth writing.
2. **Plans change constantly.** A migration, a security rule or one observation session can redirect the work. Comfort with ambiguity is a core skill.
3. **Honesty builds trust.** Showing the failures on Friday made the director *more* confident, not less.
4. **Measurement is everything.** "88% on 80 real claims" is a fact you can act on. "It works pretty well" isn't.
5. **FDEs feed the product.** Friday's note to the product team is how one customer's problem becomes everyone's feature.

## The hard parts nobody advertises

- Waiting days or weeks for data access or a firewall rule
- Context switching between meetings and deep technical work
- Working in codebases and systems with little documentation
- Travel or time-zone overlap with the customer (depending on the role)
- Being the person who has to say "that's not possible in this timeline"

If these sound energizing rather than draining, the role may suit you well.

## Check yourself

Look at Tuesday. What would have happened if the FDE had skipped the observation session and built a "summarize the whole document" feature?

Next: [Lesson 05 — The engagement lifecycle](05-engagement-lifecycle.md)
