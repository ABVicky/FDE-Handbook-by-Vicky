# Module 04 Build — AdmitFlow v1: the counsellor dashboard

**Time:** weeks 2–5, about 35–45 hours · **Capabilities:** C2

## Scenario

The CLI proved the data can be cleaned and combined. Mr. Fernandes now wants his six counsellors using it **daily**, starting with a two-week pilot. Ms. Chen (finance) has one condition: *"Each counsellor sees what they need and nothing they shouldn't. Students' details must not leak."*

You'll turn the CLI into a web application: a FastAPI backend and a React + TypeScript dashboard.

## Requirements agreed with the client

**Users:** counsellors (6), admin (Mr. Fernandes).

| ID | Story | Priority | Acceptance criteria |
| --- | --- | --- | --- |
| US-01 | As a counsellor, I log in with my own account | Must | Wrong credentials → one generic message; session lasts a working day |
| US-02 | As a counsellor, I see all leads, newest first, and can filter by status and channel and search | Must | 20–25 per page; search matches name, phone, email, course |
| US-03 | As a counsellor, I can show only my leads | Must | "Only mine" shows leads assigned to me |
| US-04 | As a counsellor, I open a lead and see its details and history | Must | Notes newest-last with author and time |
| US-05 | As a counsellor, I add a note after each call | Must | Empty notes rejected; HTML in notes shown as text |
| US-06 | As a counsellor, I change a lead's status | Must | Only valid statuses; can't change leads assigned to someone else |
| US-07 | As an admin, I assign leads to counsellors | Must | Counsellors can't assign; unknown counsellor → error |
| US-08 | As a counsellor, I schedule follow-ups and see what's due in the next 24h | Should | Only my own follow-ups; can mark done |
| US-09 | As reception, I add a phone/walk-in enquiry | Should | Name, phone/email validated; existing person merged, not duplicated |
| US-10 | As the director, I see counts by status and channel | Could | `GET /stats` |

**Non-functional:** works on a laptop browser and a phone; all personal data behind login; deployable by a part-time IT admin; API documented.

## Technical requirements

### Backend (`admitflow/api/`)
- FastAPI app factory `create_app(repo=None)`
- Pydantic request/response models; one consistent error format
- Storage behind a `Repository` interface (`JsonRepository` for now, PostgreSQL in Module 05)
- Passwords hashed (PBKDF2/bcrypt/Argon2); JWT (or session) auth; secret key from the environment, required
- Roles: `counsellor`, `admin`, enforced server-side
- Request-ID middleware with structured request logs
- CORS configured from an environment variable
- CLI commands: `admitflow create-user`, `admitflow serve`

### Frontend (`web/`)
- Vite + React + TypeScript (`strict`)
- One API client module; types mirroring the API schemas
- Screens: login, lead list (filters, search, pagination), lead detail (notes, status, follow-ups)
- Loading, error and empty states everywhere; `401` → back to login
- At least one test (Vitest)

### Quality
- API integration tests including **401, 403 and 422 cases for every relevant endpoint**; ≥ 80% coverage
- At least two ADRs (e.g. storage interface, auth approach, time zones)
- README: setup, configuration variables, how to run both parts, how to test
- Built through pull requests

## Suggested order (one PR each)

1. Repository interface + JSON implementation, with tests
2. Auth: hashing, tokens, `create-user`, `/auth/login`, `/me`
3. Lead endpoints: list/filter/paginate, detail, update with role rules
4. Notes, follow-ups, stats
5. Middleware, error format, CORS
6. Frontend: login → list → detail
7. Docs: README, ADRs, API workflow doc

## Running the reference solution

```bash
cd projects/admitflow
```

```bash
python -m pip install -e ".[api,dev]"
```

```bash
export ADMITFLOW_SECRET_KEY=$(python -c 'import secrets; print(secrets.token_urlsafe(48))')
```

```bash
admitflow import --website data/leads_sample.csv --ads data/ad_leads.csv --walkins data/walkins.csv
```

```bash
admitflow create-user priya --full-name "Priya Nair"
```

```bash
admitflow serve
```

In another terminal:

```bash
cd projects/admitflow/web && npm install && npm run dev
```

Open http://localhost:5173 and log in. The API docs are at http://localhost:8000/docs.

## Done when

- [ ] All **Must** stories pass their acceptance criteria, demonstrated end to end in the browser
- [ ] Unauthenticated requests to every non-health endpoint return `401` (tested)
- [ ] Role rules return `403` (tested)
- [ ] Bad input returns `422` naming the field (tested)
- [ ] A note containing `<script>` or `<b>` displays as plain text
- [ ] `npm run build` (type-check + build) and `npm test` pass
- [ ] ≥ 80% backend coverage; two or more ADRs; README complete

## Stretch

- `GET /leads/{id}/followups`, and show them in the detail panel
- Admin screen to assign leads in bulk
- Playwright end-to-end test: log in → open lead → add note
- Generate `types.ts` from `/openapi.json`
- Rate-limit `/auth/login` (5 attempts per minute per username)

## Reference solution

- Backend: [`projects/admitflow/admitflow/api/`](../../projects/admitflow/admitflow/api/__init__.py), [`repository.py`](../../projects/admitflow/admitflow/repository.py), [`auth.py`](../../projects/admitflow/admitflow/auth.py), tests in [`tests/test_api.py`](../../projects/admitflow/tests/test_api.py)
- Frontend: [`projects/admitflow/web/`](../../projects/admitflow/web/src/App.tsx)
- Decisions: [`docs/adr/`](../../projects/admitflow/docs/adr/001-repository-interface.md)

Two real bugs were caught while building the reference, both worth checking for in your own build:
1. The CLI and API wrote the store in different shapes, so a CLI import after creating users would have erased the users. A test now runs both against one store.
2. Follow-up times sent with a time zone (`…Z`) had the offset *dropped* instead of converted, shifting them by hours. A test now runs under two time zones.
