# Lesson 11 — Type hints

**Time:** ~2 hours · **Core**

## Why this matters

When you inherit a client's codebase, the first question about every function is "what does it take, and what does it return?" Type hints answer that in the code itself, and let tools catch mistakes before you run anything.

## The basics

```python
def priority(hours_waiting: float) -> str:
    ...

count: int = 0
names: list[str] = []          # Python 3.9+
by_id: dict[str, "Lead"] = {}
```

Hints **don't change how Python runs**. They're for readers, editors and checkers.

## Optional values and unions

```python
from typing import Optional

def normalize_phone(value: Optional[str]) -> Optional[str]:
    """Returns None if the number isn't usable."""
```

`Optional[str]` means "a `str` or `None`". In Python 3.10+, you can also write `str | None`. To use that newer style on 3.9, put this at the very top of the file (the AdmitFlow code does):

```python
from __future__ import annotations
```

## Common types

| Hint | Meaning |
| --- | --- |
| `list[str]` / `List[str]` | List of strings |
| `dict[str, int]` | Dict with string keys and int values |
| `tuple[int, str]` | Exactly an int then a str |
| `Optional[X]` | X or None |
| `Iterator[X]` | Something you can loop over that yields X |
| `Callable[[dict], Lead]` | A function taking a dict and returning a Lead |
| `Any` | Anything (use sparingly) |

## Checking types

[mypy](https://mypy.readthedocs.io/) reads your hints and reports mismatches without running the code:

```bash
python -m pip install mypy
```

```bash
mypy admitflow/
```

```python
def greet(name: str) -> str:
    return "Hi " + name

greet(None)   # mypy: Argument 1 has incompatible type "None"; expected "str"
```

VS Code's Python extension shows many of these problems as you type.

## How much to annotate

- **Always:** function parameters and return types in code others will read.
- **Usually not needed:** local variables, where the type is obvious (`count = 0`).
- Hints are documentation that can't silently go out of date, because the checker complains.

## Check yourself

Add type hints to this function, then run mypy on it:
```python
def count_by_source(leads, sources=None):
    counts = {}
    for lead in leads:
        for s in lead["sources"]:
            if sources is None or s in sources:
                counts[s] = counts.get(s, 0) + 1
    return counts
```

Next: [Lesson 12 — Testing with pytest](12-testing-with-pytest.md)
