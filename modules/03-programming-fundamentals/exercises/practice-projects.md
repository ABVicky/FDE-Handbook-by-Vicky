# Practice projects

Three small projects for extra practice, each a few evenings. Do at least one before the build, or alongside it. Put them in their own repositories; they're good early portfolio pieces.

## 1. CLI task manager

A command-line to-do list that saves tasks to a JSON file.

```bash
tasks add "Call Grace Patel" --due 2026-09-20
```

```bash
tasks list --overdue
```

```bash
tasks done 3
```

- [ ] `add`, `list`, `done`, `delete` commands using `argparse`
- [ ] Tasks stored as JSON; the file location comes from an environment variable with a sensible default
- [ ] Due dates parsed and validated; bad dates give a clear error, not a traceback
- [ ] A `Task` dataclass
- [ ] pytest tests, ≥ 80% coverage

## 2. CSV cleaner

A reusable tool that cleans any CSV given a small config file.

```bash
csvclean input.csv output.csv --config rules.json
```

`rules.json` example: `{"strip": ["name", "email"], "lower": ["email"], "required": ["email"], "dedupe_on": "email"}`

- [ ] Handles quoted fields, BOMs and non-English text correctly
- [ ] Reports rows in / rows out / rows rejected (with line numbers and reasons)
- [ ] Never silently drops a row
- [ ] Tests with deliberately messy fixture files

## 3. API information app

A small command-line app that calls a public API and summarizes the result, e.g. a weather forecast ([Open-Meteo](https://open-meteo.com/), no key needed) or public repository stats (GitHub API).

```bash
weather "Chennai" --days 3
```

- [ ] Uses `httpx` with a timeout and retries
- [ ] Handles "not found" and network errors with clear messages
- [ ] Unit tests use `httpx.MockTransport`, not the real API
- [ ] Optional: a second version in TypeScript using `fetch`

## Reflection (for each project)

Write a short README: what it does, how to run it, how to run the tests, one design decision you made and why, and one thing you'd improve. Writing this is practice for the documentation you'll hand to clients.
