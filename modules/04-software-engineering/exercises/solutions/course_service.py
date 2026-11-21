"""Exercise 02 — reference solution: a small course catalogue API.

Run:  ADMIN_TOKEN=change-me uvicorn course_service:app --reload
Test: python -m pytest -o addopts="" test_course_service.py
"""
from __future__ import annotations

import hmac
import os
from typing import Dict, List, Literal, Optional

from fastapi import Depends, FastAPI, Header, HTTPException, Query
from pydantic import BaseModel, Field

Campus = Literal["North", "South"]


class CourseIn(BaseModel):
    code: str = Field(pattern=r"^[A-Z0-9]{2,10}$")
    name: str = Field(min_length=1, max_length=120)
    campus: Campus
    fee: int = Field(gt=0)
    seats: int = Field(ge=1, le=200)


class CourseUpdate(BaseModel):
    fee: Optional[int] = Field(default=None, gt=0)
    seats: Optional[int] = Field(default=None, ge=1, le=200)


class CoursePage(BaseModel):
    items: List[CourseIn]
    total: int


def create_app(admin_token: Optional[str] = None) -> FastAPI:
    token = admin_token or os.environ.get("ADMIN_TOKEN")
    if not token:
        raise RuntimeError("Set ADMIN_TOKEN")
    app = FastAPI(title="Course catalogue")
    courses: Dict[str, CourseIn] = {}

    def require_admin(authorization: Optional[str] = Header(default=None)) -> None:
        expected = f"Bearer {token}"
        if authorization is None or not hmac.compare_digest(authorization, expected):
            raise HTTPException(401, "Admin token required", headers={"WWW-Authenticate": "Bearer"})

    def get_or_404(code: str) -> CourseIn:
        if code not in courses:
            raise HTTPException(404, f"Course {code} not found")
        return courses[code]

    @app.get("/courses", response_model=CoursePage)
    def list_courses(
        campus: Optional[Campus] = None,
        page: int = Query(1, ge=1),
        page_size: int = Query(20, ge=1, le=50),
    ):
        items = sorted((c for c in courses.values() if campus is None or c.campus == campus), key=lambda c: c.code)
        start = (page - 1) * page_size
        return {"items": items[start : start + page_size], "total": len(items)}

    @app.get("/courses/{code}", response_model=CourseIn)
    def get_course(code: str):
        return get_or_404(code)

    @app.post("/courses", response_model=CourseIn, status_code=201, dependencies=[Depends(require_admin)])
    def create_course(body: CourseIn):
        if body.code in courses:
            raise HTTPException(409, f"Course {body.code} already exists")
        courses[body.code] = body
        return body

    @app.patch("/courses/{code}", response_model=CourseIn, dependencies=[Depends(require_admin)])
    def update_course(code: str, body: CourseUpdate):
        course = get_or_404(code)
        updated = course.model_copy(update=body.model_dump(exclude_unset=True, exclude_none=True))
        courses[code] = updated
        return updated

    return app


if os.environ.get("ADMIN_TOKEN"):  # only build the module-level app when configured
    app = create_app()
