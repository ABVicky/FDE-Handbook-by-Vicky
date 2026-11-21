# Take-home projects

Typical brief: "Build a small service that ingests this data, exposes an API, and uses an LLM for X. 4–6 hours."

## What reviewers actually look at
1. **README first:** how to run it in one command, what you built, what you didn't, and why
2. **Correctness on messy input:** they will feed it edge cases
3. **Tests** for the important behaviour, not 100% coverage
4. **Judgement:** sensible scope, simple design, honest trade-offs
5. **AI evaluation:** even 15 test cases with results beats none

## A plan for a 5-hour take-home
| Time | Do |
| --- | --- |
| 0:00–0:30 | Read carefully; write assumptions and questions (send questions if allowed); sketch the design |
| 0:30–3:00 | Core path end to end, with tests, on real sample data |
| 3:00–4:00 | Edge cases, error handling, a small evaluation for the AI part |
| 4:00–4:45 | README: setup, design, trade-offs, what you'd do next with more time |
| 4:45–5:00 | Run from a clean clone; fix what breaks |

Don't over-build. A small, correct, well-explained solution beats a large, fragile one.
