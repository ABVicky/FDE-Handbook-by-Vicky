# Lesson 10 — Classes and dataclasses

**Time:** ~4 hours · **Core**

## Why this matters

Passing dicts like `{"name": ..., "phone": ...}` everywhere works until someone types `lead["phnoe"]`. A **class** gives your data a defined shape and lets you keep related behaviour next to it.

## A class in plain Python

```python
class Lead:
    def __init__(self, lead_id, name, email=None):
        self.lead_id = lead_id
        self.name = name
        self.email = email

    def display_name(self):
        return f"{self.name} ({self.lead_id})"

grace = Lead("ENQ-0001", "Grace Patel")
grace.display_name()   # "Grace Patel (ENQ-0001)"
```

- A **class** is a blueprint; `grace` is an **instance** (an object).
- `__init__` runs when you create one; `self` is the instance itself.
- **Attributes** (`self.name`) hold data; **methods** (`display_name`) are functions that belong to the object.

## Dataclasses: the practical default

For classes that mainly hold data, `@dataclass` writes `__init__`, a readable `repr`, and equality for you:

```python
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional

@dataclass
class Lead:
    lead_id: str
    received_at: datetime
    name: str
    email: Optional[str] = None
    sources: List[str] = field(default_factory=list)   # never `= []` (Lesson 04's trap)

    def matches(self, text: str) -> bool:
        return text.casefold() in self.name.casefold()

lead = Lead("ENQ-0001", datetime(2026, 9, 1, 10, 55), "Grace Patel", sources=["website"])
print(lead)
# Lead(lead_id='ENQ-0001', received_at=datetime.datetime(2026, 9, 1, 10, 55), name='Grace Patel', email=None, sources=['website'])
```

This is essentially the `Lead` in [`projects/admitflow/admitflow/models.py`](../../../projects/admitflow/admitflow/models.py), which also has `to_dict` / `from_dict` for saving to JSON.

## Class methods: alternative constructors

```python
    @classmethod
    def from_dict(cls, data):
        data = dict(data)
        data["received_at"] = datetime.fromisoformat(data["received_at"])
        return cls(**data)
```

`cls(**data)` unpacks a dict into keyword arguments.

## Inheritance and composition: use sparingly

**Inheritance** creates a specialized version of a class:

```python
class Importer:
    def parse(self, row):
        raise NotImplementedError

class WebsiteImporter(Importer):
    def parse(self, row):
        ...
```

It's useful, but deep inheritance trees are hard to follow, especially for whoever maintains your code after handover. **Prefer composition**: build objects out of smaller pieces, or just use plain functions. The AdmitFlow importers are simply a dict of functions:

```python
FORMATS = {"website": _website, "ads": _ads, "walkins": _walkins}
parse = FORMATS[fmt]
```

**Rule of thumb:** use a dataclass for data, functions for behaviour, and a full class when you have data *and* behaviour that genuinely belong together (e.g. an API client holding a session and credentials).

## Polymorphism, briefly

Different objects responding to the same method call: anything with a `.parse(row)` method can be used by code that calls `.parse(row)`. Python cares what an object *can do*, not what it *is* ("duck typing").

## Check yourself

Create a `@dataclass` called `FollowUp` with `lead_id`, `due` (datetime), `counsellor`, and `done` (default `False`). Add a method `is_overdue(now)` that returns `True` if it isn't done and `due` is before `now`.

Next: [Lesson 11 — Type hints](11-type-hints.md)
