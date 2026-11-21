"""Follow-up reminder service (fixed version).

Stores follow-up reminders in memory and exposes them over HTTP.
All endpoints require `Authorization: Bearer <FOLLOWUP_TOKEN>`.
All times are stored as timezone-aware UTC.
"""
import os
from datetime import datetime, timezone
from typing import Optional

from fastapi import Depends, FastAPI, Header, HTTPException, Query
from pydantic import BaseModel, field_validator

TOKEN = os.environ.get("FOLLOWUP_TOKEN", "dev-token")


def require_token(authorization: Optional[str] = Header(default=None)) -> None:
    if authorization != f"Bearer {TOKEN}":
        raise HTTPException(401, "unauthorized")


# Fix 4: the token check is applied to the whole app, so a new route can't forget it.
app = FastAPI(title="Follow-up service", dependencies=[Depends(require_token)])
DB = {}


class FollowUpIn(BaseModel):
    lead_id: str
    due: datetime
    who: str

    @field_validator("due")
    @classmethod
    def to_utc(cls, value: datetime) -> datetime:
        # Fix 3: store every time as aware UTC. Naive input is treated as UTC (documented in README).
        return value.replace(tzinfo=timezone.utc) if value.tzinfo is None else value.astimezone(timezone.utc)


@app.post("/followups", status_code=201)  # Fix 1: creating something returns 201 Created
def create_followup(body: FollowUpIn):
    followup_id = str(len(DB) + 1)
    DB[followup_id] = {"id": followup_id, **body.model_dump()}
    return DB[followup_id]


@app.get("/followups")
def list_followups(page: int = Query(1, ge=1), size: int = Query(10, ge=1, le=100)):
    rows = sorted(DB.values(), key=lambda r: r["due"])
    start = (page - 1) * size  # Fix 2: pages are numbered from 1
    return rows[start : start + size]


@app.get("/followups/overdue")
def overdue_followups():
    now = datetime.now(timezone.utc)
    return [r for r in DB.values() if r["due"] < now]


@app.delete("/followups/{followup_id}")
def delete_followup(followup_id: str):
    if followup_id not in DB:
        raise HTTPException(404, "not found")
    del DB[followup_id]
    return {"deleted": followup_id}
