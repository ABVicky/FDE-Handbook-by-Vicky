# Lesson 03 — FastAPI fundamentals

**Time:** ~6 hours · **Core**

## Why FastAPI

[FastAPI](https://fastapi.tiangolo.com/) is a Python web framework that uses type hints for validation and documentation. It's widely used for AI and data services, which is a large share of FDE work. (Flask and Django are also common; the concepts carry over.)

```bash
python -m pip install "fastapi>=0.115" "uvicorn>=0.30"
```

## Hello, API

```python
# main.py
from fastapi import FastAPI

app = FastAPI(title="Hello")

@app.get("/health")
def health():
    return {"status": "ok"}
```

```bash
uvicorn main:app --reload
```

Open http://localhost:8000/health, then **http://localhost:8000/docs** for interactive documentation you didn't have to write.

## Path and query parameters

```python
from typing import Optional
from fastapi import Query

@app.get("/leads/{lead_id}")
def get_lead(lead_id: str):
    ...

@app.get("/leads")
def list_leads(
    status: Optional[str] = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=25, ge=1, le=100),
):
    ...
```

`page=abc` or `page_size=5000` automatically returns `422` with a clear message.

## Request bodies with Pydantic

```python
from typing import Literal, Optional
from pydantic import BaseModel, Field, field_validator

class LeadCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    phone: Optional[str] = None
    source: Literal["website", "ad", "phone", "walk-in", "whatsapp"]

    @field_validator("name")
    @classmethod
    def has_a_letter(cls, value: str) -> str:
        if not any(ch.isalpha() for ch in value):
            raise ValueError("name must contain at least one letter")
        return value.strip()

@app.post("/leads", status_code=201)
def create_lead(body: LeadCreate):
    return {"name": body.name, "source": body.source}
```

Pydantic parses JSON, converts types, runs your validators, and returns field-level `422` errors. Inside the function, `body` is guaranteed valid.

## Response models

```python
class LeadOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)   # build from dataclasses/objects
    lead_id: str
    name: str
    status: str

@app.get("/leads/{lead_id}", response_model=LeadOut)
def get_lead(lead_id: str):
    return repo.get_lead(lead_id)    # extra fields (e.g. password hashes) are filtered out
```

A response model documents the output *and* acts as a filter, so internal fields never leak by accident.

## Dependency injection with `Depends`

Dependencies are functions FastAPI calls for you, per request:

```python
from fastapi import Depends, Request

def get_repo(request: Request):
    return request.app.state.repo

@app.get("/stats")
def stats(repo = Depends(get_repo)):
    ...
```

They're perfect for shared concerns: the data store, the current user, permission checks. In tests you can swap them. Read [`admitflow/api/deps.py`](../../../projects/admitflow/admitflow/api/deps.py) to see `get_repo`, `current_user` and `require_admin`.

## Organizing a real app

```
admitflow/api/
├── __init__.py   # create_app(): middleware, error handlers, include routers
├── deps.py       # dependencies: repo, current user, roles
├── schemas.py    # Pydantic request/response models
└── routes.py     # the endpoints (APIRouter)
```

An **app factory** (`create_app(repo=None)`) lets tests create an app with a temporary store:

```python
from fastapi.testclient import TestClient
client = TestClient(create_app(JsonRepository(tmp_path / "store.json")))
```

## Sync or async routes?

FastAPI supports both `def` and `async def` routes. Use `async def` only if everything inside is non-blocking (async database driver, `httpx.AsyncClient`). Plain `def` routes run in a thread pool, which is the safe default when you call blocking code, as AdmitFlow's JSON store does.

*Stretch:* Node.js + Express is the JavaScript equivalent; Django offers a "batteries-included" alternative with an admin UI and ORM. Build the health endpoint in one of them for comparison.

## Check yourself

Add `GET /leads/{lead_id}/followups` to your build: it returns all follow-ups for one lead, `404` if the lead doesn't exist, and requires login. Write the test first.

Next: [Lesson 04 — Authentication and authorization](04-auth.md)
