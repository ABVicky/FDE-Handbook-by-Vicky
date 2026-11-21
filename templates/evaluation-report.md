# Evaluation Report — <AI feature>

**Version evaluated:** (code commit, model ID, prompt version, document set date) · **Date:** · **Author:**

## 1. What was evaluated and why
<Feature, its users, and the decision this report supports (e.g. "switch the assistant to Claude for the public website").>

## 2. Test set
| Property | Value |
| --- | --- |
| Number of cases | |
| Where they came from | real questions / transcripts / synthesized, and how they were reviewed |
| Categories and counts | answerable by topic, unanswerable, prompt injection, outdated information… |
| Held-out cases (never used for tuning) | |

## 3. Metrics and results
| Metric | Definition | Bar | Result | Previous |
| --- | --- | --- | --- | --- |
| Correct | passes all checks for the case | | | |
| Retrieval@k | expected source in top k | | | |
| Correct declines | says "I don't know" when it should | | | |
| Groundedness | every claim supported by a cited source | | | |
| Latency (p50 / p95) | | | | |
| Cost per 1,000 questions | | | | |

## 4. Failures, examined
For each failure (or a sample): question, answer, expected, root cause (retrieval / answer / data / test), action.

## 5. Risks and limitations
<What the evaluation does not cover; known weak areas; how users could be harmed.>

## 6. Recommendation
<Ship / don't ship / ship with conditions, and what monitoring is needed after launch.>

*Worked example: [Module 08 build](../modules/08-generative-ai-engineering/build.md) and `admitflow eval-assistant`.*
