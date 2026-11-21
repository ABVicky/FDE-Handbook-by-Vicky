# Module 04 — Field Track: Scope and estimate before you build

**Time:** ~2 hours before the build, 1 hour after · **Capabilities:** C1, C5

## Why

"How long will it take?" is the question every client asks, and the one engineers most often get wrong. Wrong estimates aren't the real problem; **hidden assumptions** are. An FDE who writes down scope, assumptions and risks, and updates them honestly, keeps the client's trust even when things take longer.

## Part 1: before the build (≈ 2 h)

Using the [build requirements](build.md#requirements-agreed-with-the-client), write `my-work/field-track/m04-estimate.md`:

1. **Scope table**: break each story into tasks you could finish in half a day or less.

   | Story | Task | Estimate (hours) | Confidence (H/M/L) |
   | --- | --- | --- | --- |

2. **Totals** for Must / Should / Could stories.
3. **Assumptions** (at least five), e.g. "The JSON store is acceptable for the pilot", "Counsellors use Chrome or Edge", "No SSO needed for the pilot."
4. **Risks** (at least three), each with a mitigation.
5. **Proposal email** to Mr. Fernandes (≤ 150 words): what will be ready for the pilot, what won't, and what you need from him (e.g. counsellor names for accounts, a date for a 30-minute demo).

Estimating tips:
- Estimate in ranges ("6–10 h") when confidence is low.
- Include the invisible work: tests, reviews, docs, deployment, the demo itself.
- Compare with something you've done before (your Module 03 build).

## Part 2: during the build

Log actual hours per task in the same table (add an "Actual" column).

## Part 3: after the build (≈ 1 h)

Add a **retrospective** section:
- Which tasks were most under-estimated? Why?
- Which assumptions turned out wrong?
- What would you tell the client differently next time?
- Your personal "multiplier": actual ÷ estimate. Use it next time.

## Done when

- [ ] Estimate written **before** starting the build (commit it first: the Git timestamp proves it)
- [ ] Actuals logged
- [ ] Retrospective with your multiplier and at least three lessons
