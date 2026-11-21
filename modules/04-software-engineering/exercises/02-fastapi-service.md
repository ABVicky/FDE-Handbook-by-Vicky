# Exercise 02 — A FastAPI course catalogue with auth and tests

Build a small standalone service, `course_service.py`:

| Endpoint | Who | Behaviour |
| --- | --- | --- |
| `GET /courses` | Anyone | List courses, `?campus=` filter, paginated (`page`, `page_size` ≤ 50), returns `{items, total}` |
| `GET /courses/{code}` | Anyone | One course or `404` |
| `POST /courses` | Admin token only | Create: `code` (2–10 uppercase letters/digits), `name`, `campus` (`North`/`South`), `fee` (> 0, whole currency units), `seats` (1–200). `201`; `409` if the code exists |
| `PATCH /courses/{code}` | Admin token only | Update `fee` and/or `seats`; validates the same rules |

Rules:
- Admin auth: `Authorization: Bearer <ADMIN_TOKEN>` where `ADMIN_TOKEN` comes from an environment variable (no default in production code!). Missing/wrong → `401`.
- Use Pydantic models for input and output.
- Store courses in a dict inside an app factory `create_app()`, so each test gets a fresh app.

Then write **at least 10 tests** with `TestClient`, covering: happy paths, `401`, `404`, `409`, `422` for each validation rule, pagination limits.
