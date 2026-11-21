# Debugging unfamiliar code

Many FDE interviews hand you a small codebase with a failing test or a bug report, and watch how you work. They're assessing **method**, not speed.

## The method (say each step out loud)
1. **Reproduce** the problem; read the full error.
2. **Read the test or report** for intended behaviour.
3. **Find the entry point** and follow one input through the code.
4. **Form a hypothesis**, then test it with one change, a print or a debugger breakpoint.
5. **Fix the cause, not the symptom**; add a test that fails without the fix.
6. **Look for siblings:** does the same mistake exist elsewhere?

## Practise with the handbook's break & fix exercises
Each is a realistic "you inherited this" scenario. Time yourself (45 minutes), talk out loud, and compare with the solution:

| Exercise | Skill |
| --- | --- |
| [Module 02: it won't start](../modules/02-computing-foundations/break-and-fix/README.md) | Environment, permissions, ports |
| [Module 03: names silently dropped](../modules/03-programming-fundamentals/break-and-fix/README.md) | Silent data loss, Unicode |
| [Module 04: inherited service](../modules/04-software-engineering/break-and-fix/README.md) | Failing tests, a hidden security hole |
| [Module 05: slow report](../modules/05-databases-and-data-engineering/break-and-fix/README.md) | Query plans, indexes |
| [Module 06: works on my laptop](../modules/06-cloud-and-infrastructure/break-and-fix/README.md) | Diagnosis from logs only |
| [Module 07: the 99% model](../modules/07-ai-and-machine-learning/break-and-fix/README.md) | Leakage, evaluation |
| [Module 08: last year's fees](../modules/08-generative-ai-engineering/break-and-fix/README.md) | RAG data and retrieval |
| [Module 09: duplicate contacts](../modules/09-enterprise-integration/break-and-fix/README.md) | Idempotency |
| [Module 10: silent outbox](../modules/10-production-security-reliability/break-and-fix/README.md) | Monitoring, incidents |
