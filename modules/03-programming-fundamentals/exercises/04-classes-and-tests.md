# Exercise set 04 — Classes and tests

Counsellors need follow-up reminders. Build them in `my-work/m03/followup.py` with tests in `my-work/m03/test_followup.py`.

1. **`FollowUp` dataclass** with `lead_id: str`, `due: datetime`, `counsellor: str`, `done: bool = False`, and `notes: list[str]` (use `field(default_factory=list)`).
2. **`is_overdue(self, now)`**: `True` if not done and `due < now`.
3. **`complete(self, note)`**: mark done and append the note. Completing twice should raise `ValueError("already done")`.
4. **`overdue(followups, now)`**: a function returning overdue follow-ups sorted by `due`, oldest first.
5. **`per_counsellor(followups, now)`**: `{counsellor: number overdue}`.
6. **Tests** (pytest): at least 8 tests, including:
   - a follow-up due exactly at `now` is **not** overdue
   - a done follow-up is never overdue
   - completing twice raises `ValueError` (use `pytest.raises`)
   - two `FollowUp` objects don't share the same `notes` list
   - `overdue` sorts correctly
   - use `@pytest.mark.parametrize` at least once
7. Run with coverage. Get to 100% for this small module:
   ```bash
   pytest --cov=followup --cov-report=term-missing
   ```
