# Lesson 09 — Engineering practice: structure, reviews, docs, unfamiliar code

**Time:** ~4 hours · **Core**

## Why this matters

An FDE's code outlives the engagement. Someone at the client will maintain it, probably someone with less context than you. Structure, documentation and review habits decide whether the system survives the handover.

## Structure: separate the layers

```
admitflow/
├── normalize.py, dedupe.py     ← domain logic: pure, no I/O, easiest to test
├── models.py                   ← data shapes
├── repository.py, store.py     ← storage behind an interface
├── importers.py                ← reading external formats
├── auth.py                     ← security primitives
├── api/                        ← HTTP layer: thin, calls the layers above
└── cli.py                      ← command-line layer: also thin
```

Rule: **business rules don't import web frameworks.** `dedupe.py` knows nothing about FastAPI, so the CLI, the API and a future batch job all reuse it.

A few principles worth knowing by name (no need to memorize the acronyms):
- **Single responsibility:** each module has one reason to change.
- **Depend on interfaces, not details:** routes use `Repository`, not "a JSON file" ([ADR-001](../../../projects/admitflow/docs/adr/001-repository-interface.md)).
- **Keep it simple:** the simplest design that meets today's requirements, with room to change.

*Stretch:* read about the **SOLID** principles and common **design patterns** (repository, factory, strategy, adapter). You've already used repository, factory (`create_app`) and strategy (the `FORMATS` dict of importers).

## Requirements before code

Turn the client's needs into user stories with **testable acceptance criteria** ([template](../../../templates/requirements.md)):

> **US-03** As a counsellor, I want to see only my leads so I can plan my calls.
> *Given* I'm logged in as Priya *when* I tick "Only mine" *then* I see only leads assigned to me, newest first.

An acceptance criterion maps directly onto a test (`test_mine_filter`).

## Decisions: write ADRs

An **Architecture Decision Record** captures *why* you chose something: context, decision, consequences, alternatives ([template](../../../templates/adr.md)). Three ADRs written for AdmitFlow:
- [001: repository interface](../../../projects/admitflow/docs/adr/001-repository-interface.md)
- [002: local time](../../../projects/admitflow/docs/adr/002-local-time.md)
- [003: token auth](../../../projects/admitflow/docs/adr/003-token-auth.md)

Six months later, "why on earth is it like this?" has an answer.

## Code review

**As an author:**
- Small pull requests (under ~400 lines changed) get real reviews; huge ones get rubber stamps.
- The description says *what*, *why*, and *how it was tested*.
- Review your own diff first. You'll find half the problems.

**As a reviewer:**
- Look for, in order: correctness, security (auth, input validation, secrets), tests, clarity, then style.
- Ask questions rather than issue orders: "What happens if `due` has a time zone?"
- Approve when it's better than before and safe, not when it's how *you* would have written it.

Automate style (formatters like `ruff format` / Prettier, linters like `ruff` / ESLint) so humans review substance.

## Working in an unfamiliar codebase

You'll do this at nearly every client. A routine:

1. **Run it.** Find the README (or the lack of one), get it running locally, run the tests.
2. **Map it.** Entry points, main modules, where data comes from and goes. Draw it.
3. **Follow one request end to end** with a debugger or logs.
4. **Read the tests** for intended behaviour, and the Git history (`git log -p path/`) for *why*.
5. **Make a small, safe change** with a test.
6. **Leave it better:** write down what you learned (README, comments, an ADR).

The [break & fix](../break-and-fix/README.md) is exactly this situation: no README, failing tests, a hidden security hole.

## Documentation that gets read

| Document | Audience | Contents |
| --- | --- | --- |
| README | Next developer | What it is, how to run, test, configure, deploy |
| API docs | Integrators | Auto-generated reference + workflows ([template](../../../templates/api-documentation.md)) |
| ADRs | Future maintainers | Why key decisions were made |
| Design doc | Reviewers, client IT | Architecture, data, security ([template](../../../templates/technical-design.md)) |

## The software development lifecycle, FDE-style

Short loops: **agree a small slice → build → demo to real users → adjust**. Ship something a counsellor can use in week 2, not everything in week 10. You'll formalize this in Module 11.

## Check yourself

Pick any open-source Python project you've never seen (or a colleague's project). Spend 45 minutes following steps 1–4 above, and write a one-page "map" of it.

Next: [Exercises](../exercises/README.md) and the [build](../build.md).
