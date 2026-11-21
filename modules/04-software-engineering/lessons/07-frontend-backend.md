# Lesson 07 — Connecting frontend and backend

**Time:** ~4 hours · **Core**

## One API client module

Put every HTTP call in one file (`web/src/api.ts`), so auth headers, base URLs and error handling live in one place:

```ts
const BASE_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

export class ApiError extends Error {
  constructor(public status: number, message: string) { super(message); }
}

export async function request<T>(path: string, options: RequestInit = {}, token?: string): Promise<T> {
  const headers: Record<string, string> = { "Content-Type": "application/json" };
  if (token) headers.Authorization = `Bearer ${token}`;
  let response: Response;
  try {
    response = await fetch(`${BASE_URL}${path}`, { ...options, headers });
  } catch {
    throw new ApiError(0, "Can't reach the AdmitFlow server. Check your connection.");
  }
  const body = await response.json().catch(() => null);
  if (!response.ok) throw new ApiError(response.status, body?.error?.detail ?? "Request failed");
  return body as T;
}
```

Components then call `api.leads(token, {...})` and never think about headers.

## Configuration per environment

The API's address differs on your laptop, in staging and in production. Vite reads `VITE_*` variables from `.env` files:

```
# .env.local (not committed)
VITE_API_URL=http://localhost:8000
```

Commit a `.env.example`. Remember: **everything in frontend code is public**. Never put secrets (API keys) in `VITE_*` variables. The browser downloads them.

## CORS: why the browser blocks your request

Your dashboard runs at `http://localhost:5173` and the API at `http://localhost:8000`. Different ports are different **origins**, and browsers block cross-origin requests unless the server explicitly allows them:

```
Access to fetch at 'http://localhost:8000/auth/login' from origin 'http://localhost:5173'
has been blocked by CORS policy
```

Fix it on the **server**:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],          # from configuration, per environment
    allow_methods=["GET", "POST", "PATCH"],
    allow_headers=["Authorization", "Content-Type"],
)
```

Never use `allow_origins=["*"]` with credentials on a system holding personal data. List the real dashboard origin(s).

**Debugging tip:** a CORS failure looks like a network error to your JavaScript. The real reason is only in the browser console. Also check that the API is actually running on that port. While testing this module's reference app, an old process was still holding port 8000, so the "API" answering was a different program with no CORS headers at all. `lsof -i :8000` found it in seconds (Module 02).

## Where to keep the token

| Option | Survives refresh | Readable by JS (XSS risk) | Sent automatically (CSRF risk) |
| --- | --- | --- | --- |
| React state only | No | Yes | No |
| `sessionStorage` | Yes, until the tab closes | Yes | No |
| `localStorage` | Yes, indefinitely | Yes | No |
| `HttpOnly` cookie | Yes | **No** | Yes, so CSRF protection is needed |

AdmitFlow uses `sessionStorage` (a reasonable trade-off for a pilot, recorded in ADR-003). Many production systems use `HttpOnly` cookies with CSRF protection. Know the trade-offs; record your choice.

## Handling auth errors

When any request returns `401`, the session is over: clear it and show the login screen.

```ts
catch (err) {
  if (err instanceof ApiError && err.status === 401) return onAuthError();   // → logout()
  setError(err instanceof Error ? err.message : "Failed to load leads");
}
```

`403` is different: the user *is* logged in but not allowed. Show the message; don't log them out.

## Keep types in sync

`web/src/types.ts` mirrors `admitflow/api/schemas.py`. When they drift, bugs follow. Options:
- Keep both by hand and review together (fine for small projects).
- Generate TypeScript types from FastAPI's `/openapi.json` (e.g. `openapi-typescript`). Better as the API grows.

## Running both together

Terminal 1:

```bash
export ADMITFLOW_SECRET_KEY=$(python -c 'import secrets; print(secrets.token_urlsafe(48))')
```

```bash
admitflow serve
```

Terminal 2:

```bash
cd web && npm run dev
```

## Check yourself

Stop the API while the dashboard is open, then try to open a lead. What does the user see? Is it clear what happened and what to do? Improve the message if not.

Next: [Lesson 08 — Testing strategy](08-testing-strategy.md)
