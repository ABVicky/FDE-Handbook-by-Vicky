# Break & Fix — Solution

> ⚠️ Try it properly first.

The fixed service: [`solution/app.py`](solution/app.py). The same tests, all passing: [`solution/test_app.py`](solution/test_app.py).

## The four problems

| # | Test | Symptom | Cause | Fix |
| --- | --- | --- | --- | --- |
| 1 | `test_create_returns_201` | `assert 200 == 201` | FastAPI returns 200 by default | `@app.post("/followups", status_code=201)` |
| 2 | `test_first_page_contains_earliest` | Page 1 has only 2 items | `start = page * size` skips the first page (page 1 starts at index 10) | `start = (page - 1) * size`, plus `Query(ge=1)` so `page=0` is rejected |
| 3 | `test_overdue` | `TypeError: can't compare offset-naive and offset-aware datetimes` → 500 | Request times have a time zone (`…+00:00`), but the server compares them with naive `datetime.now()` | Normalize every input to aware UTC in a validator; compare with `datetime.now(timezone.utc)` |
| 4 | `test_delete_requires_token` | Delete works **without a token** | `@app.delete` is the only route missing `dependencies=[Depends(check)]` | Apply the dependency to the **whole app**: `FastAPI(dependencies=[Depends(require_token)])` |

## Why #4 is the serious one

Anyone who can reach the service can delete every follow-up with a loop of `curl -X DELETE …/followups/1`, `/2`, … Counsellors would silently stop getting reminders, and students would stop being called. Nothing would look broken.

The deeper problem is the *pattern*: auth was added route by route, so the next developer who adds a route will probably forget it too. Making authentication the **default for the whole app** ("deny by default") fixes the class of bug, not just this instance. Public routes (like `/health`) should be the ones that need an explicit exception.

Also fixed in passing: `hmac.compare_digest` would be better than `!=` for the token comparison. The solution keeps `!=` to stay close to the original, so it's a good follow-up for you.

## Sample README (excerpt)

> # Follow-up reminder service
> Stores follow-up reminders for counsellors and lists those that are overdue.
>
> **Configuration:** `FOLLOWUP_TOKEN` (required in production): the bearer token every request must send.
> **Run:** `pip install fastapi uvicorn` then `uvicorn app:app --reload`
> **Test:** `pip install pytest httpx` then `python -m pytest test_app.py`
> **Time zones:** all times are stored as UTC. Times sent without a zone are assumed to be UTC; send `…+05:30` or `…Z` explicitly.
> **Limitations:** data is kept in memory and lost on restart; IDs restart from 1.

## Sample handover note

> Inherited follow-up service: 4 of 5 tests were failing. Fixed status codes, pagination (page 1 was skipped), and a time-zone crash on the overdue list. **The delete endpoint required no authentication**; fixed by enforcing auth app-wide. Still worrying: data lives in memory (lost on restart) and there's one shared token for everyone. Recommend folding this into AdmitFlow's API, which already has per-user auth and persistent storage.

## A note on the time-zone bug

When writing this exercise, the *first* version of the fixed service treated times without a zone as UTC, and the tests sent local times without a zone. On a machine set to India time (UTC+5:30), a follow-up due "in 5 hours" was stored as already overdue. Time-zone bugs depend on where the code runs, which is why the tests now send explicit UTC times, and why AdmitFlow's own tests run under two time zones.
