# Lesson 05 — Errors, logging, middleware and background work

**Time:** ~3 hours · **Core**

## Why this matters

When a counsellor says "it showed an error," you need to find *that* request in the logs within a minute. And when an assignment notification is slow, the counsellor shouldn't be stuck waiting for it. This lesson covers the plumbing that makes an API operable.

## Raising errors deliberately

```python
from fastapi import HTTPException

lead = repo.get_lead(lead_id)
if lead is None:
    raise HTTPException(status_code=404, detail=f"Lead {lead_id} not found")
```

Helper functions keep routes short:

```python
def _get_lead_or_404(repo, lead_id):
    lead = repo.get_lead(lead_id)
    if lead is None:
        raise HTTPException(404, f"Lead {lead_id} not found")
    return lead
```

## One error format: exception handlers

```python
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

@app.exception_handler(StarletteHTTPException)
async def http_error(request, exc):
    return JSONResponse(status_code=exc.status_code,
                        content={"error": {"status": exc.status_code, "detail": exc.detail}},
                        headers=getattr(exc, "headers", None))

@app.exception_handler(RequestValidationError)
async def validation_error(request, exc):
    problems = [{"field": ".".join(str(p) for p in e["loc"][1:]), "message": e["msg"]} for e in exc.errors()]
    return JSONResponse(status_code=422, content={"error": {"status": 422, "detail": problems}})
```

Unexpected exceptions become `500`s. Let them: log them with a stack trace, and never send stack traces to the client (they reveal internals).

## Middleware: code around every request

```python
import time, uuid

@app.middleware("http")
async def request_log(request, call_next):
    request_id = request.headers.get("X-Request-ID") or uuid.uuid4().hex[:12]
    start = time.perf_counter()
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    log.info("request_id=%s method=%s path=%s status=%s duration_ms=%.1f",
             request_id, request.method, request.url.path, response.status_code,
             (time.perf_counter() - start) * 1000)
    return response
```

The **request ID** connects a user's report ("it failed at 10:42") to exact log lines. Show it in the UI's error messages so users can quote it.

Other common middleware: **CORS** (Lesson 07), compression, security headers (Module 10).

## Structured logging

Logs written as `key=value` pairs (or JSON) can be searched and graphed:

```
request_id=3fa2c9 method=PATCH path=/leads/ENQ-0042 status=403 duration_ms=4.1
```

Never log passwords, tokens, or full personal records. Log IDs, not names and phone numbers. Module 10 builds on this with metrics and tracing.

## Background tasks

Some work shouldn't make the user wait: sending a notification, generating a report.

```python
from fastapi import BackgroundTasks

@app.patch("/leads/{lead_id}")
def update_lead(lead_id: str, body: LeadUpdate, background: BackgroundTasks, ...):
    ...
    if changes.get("assigned_to"):
        background.add_task(notify_assignment, lead_id, changes["assigned_to"])
    return lead
```

The response is sent first; the task runs afterwards **in the same process**. If the server restarts, queued tasks are lost. For work that must not be lost (sending 500 follow-up messages), use a real job queue with retries (e.g. Celery, RQ, or a cloud queue), covered in Modules 06 and 09.

## Check yourself

1. Add the request ID to every error response body in your build, and show it in the frontend's error message.
2. When would `BackgroundTasks` be the wrong choice? Give an AdmitFlow example.

Next: [Lesson 06 — Frontend fundamentals: HTML, CSS and React](06-react.md)
