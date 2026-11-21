"""AdmitFlow HTTP API (added in Module 04). Run: admitflow serve"""
from __future__ import annotations

import logging
import os
import time
import uuid
from typing import Optional

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from .. import __version__
from ..observability import metrics
from ..privacy import RedactingFilter
from ..repository import Repository, default_repository
from ..security import SECURITY_HEADERS, RateLimiter
from .routes import public, router

log = logging.getLogger("admitflow.api")


def _default_scorer():
    """Lead scoring is optional (Module 07): needs the `ml` extra and a trained model file."""
    path = os.environ.get("ADMITFLOW_MODEL", "models/lead_score.joblib")
    try:
        from ..scoring import load_scorer

        return load_scorer(path)
    except ImportError:
        return None


def create_app(repo: Optional[Repository] = None, scorer=None, assistant=None) -> FastAPI:
    from ..assistant import build_assistant

    app = FastAPI(title="AdmitFlow API", version=__version__)
    app.state.repo = repo or default_repository()
    app.state.scorer = scorer if scorer is not None else _default_scorer()
    app.state.assistant = assistant if assistant is not None else build_assistant()

    origins = os.environ.get("ADMITFLOW_CORS_ORIGINS", "http://localhost:5173").split(",")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[o.strip() for o in origins if o.strip()],
        allow_methods=["GET", "POST", "PATCH"],
        allow_headers=["Authorization", "Content-Type"],
    )

    # Module 10: limits for unauthenticated, public endpoints (per client IP; see security.py for caveats)
    app.state.public_limiter = RateLimiter(float(os.environ.get("ADMITFLOW_PUBLIC_RATE_PER_MINUTE", "30")), burst=10)
    app.state.login_limiter = RateLimiter(float(os.environ.get("ADMITFLOW_LOGIN_RATE_PER_MINUTE", "5")), burst=5)
    for handler in logging.getLogger().handlers:           # mask emails/phones in every log line
        if not any(isinstance(f, RedactingFilter) for f in handler.filters):
            handler.addFilter(RedactingFilter())

    @app.middleware("http")
    async def request_log(request: Request, call_next):
        request_id = request.headers.get("X-Request-ID") or uuid.uuid4().hex[:12]
        start = time.perf_counter()
        if request.url.path.startswith("/public/"):
            client = request.client.host if request.client else "unknown"
            allowed, wait = app.state.public_limiter.allow(client)
            if not allowed:
                metrics.inc("admitflow_rate_limited_total", help="Requests rejected by rate limiting", scope="public")
                return JSONResponse(status_code=429, headers={"Retry-After": str(int(wait) + 1), "X-Request-ID": request_id},
                                    content={"error": {"status": 429, "detail": "Too many requests. Please slow down."}})
        response = await call_next(request)
        elapsed = time.perf_counter() - start
        route = getattr(request.scope.get("route"), "path", "unmatched")   # "/leads/{lead_id}", not the raw URL
        metrics.inc("admitflow_http_requests_total", help="HTTP requests", route=route, method=request.method,
                    status=response.status_code)
        metrics.observe("admitflow_http_request_seconds", elapsed, help="HTTP request latency", route=route)
        response.headers["X-Request-ID"] = request_id
        for header, value in SECURITY_HEADERS.items():
            response.headers.setdefault(header, value)
        log.info(
            "request_id=%s method=%s path=%s status=%s duration_ms=%.1f",
            request_id, request.method, route, response.status_code, elapsed * 1000,
        )
        return response

    # One error shape for every failure, so the frontend can handle them uniformly.
    @app.exception_handler(StarletteHTTPException)
    async def http_error(request: Request, exc: StarletteHTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": {"status": exc.status_code, "detail": exc.detail}},
            headers=getattr(exc, "headers", None),
        )

    @app.exception_handler(RequestValidationError)
    async def validation_error(request: Request, exc: RequestValidationError):
        problems = [{"field": ".".join(str(p) for p in e["loc"][1:]), "message": e["msg"]} for e in exc.errors()]
        return JSONResponse(status_code=422, content={"error": {"status": 422, "detail": problems}})

    app.include_router(router)
    app.include_router(public)
    return app
