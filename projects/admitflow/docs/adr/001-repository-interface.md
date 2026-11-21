# ADR-001: Put data access behind a repository interface

**Status:** Accepted · **Date:** Module 04 · **Deciders:** FDE, Head of Admissions (informed)

## Context
The Module 03 CLI reads and writes a JSON file directly. The API (Module 04) needs the same data, and Module 05 will move it to PostgreSQL. If routes touch files directly, that move means rewriting every route.

## Decision
Routes depend on a `Repository` protocol (`admitflow/repository.py`). `JsonRepository` implements it for the pilot; `SqlRepository` will implement it for production. `default_repository()` picks one from configuration (`DATABASE_URL` set → SQL; otherwise the JSON file).

## Consequences
- ✅ Swapping storage is a configuration change, not a code change.
- ✅ Tests can use a temporary JSON repository, which is fast and needs no database.
- ⚠️ Filtering logic must behave identically in both implementations. Shared tests (`tests/test_repository_contract.py`, Module 05) enforce this.
- ⚠️ The JSON store loads the whole file per request. That's acceptable for a 6-user pilot with a few thousand leads, but not beyond.

## Alternatives considered
- **Use SQLite from the start:** simpler long-term, but adds SQL before learners have met it (Module 05).
- **An ORM everywhere:** couples routes to SQLAlchemy; harder to test.
