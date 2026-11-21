# ADR-004: Lead scoring as a tie-breaker, not a gatekeeper

**Status:** Accepted · **Date:** Module 07

## Context
Ms. Rao asked for "AI to tell counsellors which leads will enrol." We have two past intakes (3,000 leads) with outcomes. Evaluated honestly (only features known at enquiry time, trained on 2024, tested on 2025), a logistic-regression model scores ROC AUC 0.605 against 0.609 for a simple "conversion rate of the lead's source" baseline; precision in the top 20% is 15.7% vs 14.3% (base rate 10.7%). Meanwhile, the history shows leads first contacted within 24 hours enrol at ~16%, versus 2.5% after 72 hours.

## Decision
- Ship the model as an **optional, explained tie-breaker** (`/leads/priority`, `/leads/{id}/score`), labelled "experimental", showing bands (high/medium/low) and the top reasons, never a bare number.
- The priority queue puts **leads waiting over 24 hours first**, then orders by score.
- The score is **never** used to decide that a lead isn't called.
- Recommend to the client that the bigger lever is **response time**, not prediction.

## Consequences
- ✅ Honest expectations: the client hears "the model helps a little; speed helps a lot."
- ✅ Explanations make the score checkable by counsellors.
- ⚠️ The model must be re-evaluated each intake; retire it if it stops beating the baseline.
- ⚠️ Walk-in records have dates without times; the feature code treats them as in-hours (a bug found while building).

## Alternatives considered
- **No model at all:** defensible. We kept it because it modestly improves day-one call ordering (Exercise 03: ~16 more future students reached on day one per 1,500 leads), and it gives the team an evaluated pipeline to improve as data grows.
- **Use response time / contacts as features:** much higher scores, but they aren't known when the lead arrives: leakage.
