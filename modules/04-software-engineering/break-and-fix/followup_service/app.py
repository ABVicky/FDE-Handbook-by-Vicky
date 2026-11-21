import os
from datetime import datetime
from typing import Optional

from fastapi import Depends, FastAPI, Header, HTTPException
from pydantic import BaseModel

app = FastAPI()
DB = {}
TOKEN = os.environ.get("FOLLOWUP_TOKEN", "dev-token")


def check(authorization: Optional[str] = Header(default=None)):
    if authorization != f"Bearer {TOKEN}":
        raise HTTPException(401, "unauthorized")


class In(BaseModel):
    lead_id: str
    due: datetime
    who: str


@app.post("/followups", dependencies=[Depends(check)])
def create(x: In):
    i = str(len(DB) + 1)
    DB[i] = {"id": i, **x.model_dump()}
    return DB[i]


@app.get("/followups", dependencies=[Depends(check)])
def items(page: int = 1, size: int = 10):
    rows = sorted(DB.values(), key=lambda r: r["due"])
    start = page * size
    return rows[start : start + size]


@app.get("/followups/overdue", dependencies=[Depends(check)])
def overdue():
    now = datetime.now()
    return [r for r in DB.values() if r["due"] < now]


@app.delete("/followups/{i}")
def remove(i: str):
    if i not in DB:
        raise HTTPException(404, "not found")
    del DB[i]
    return {"deleted": i}
