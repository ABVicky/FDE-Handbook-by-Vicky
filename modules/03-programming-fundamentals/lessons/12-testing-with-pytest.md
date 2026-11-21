# Lesson 12 — Testing with pytest

**Time:** ~5 hours · **Core**

## Why this matters

Tests are how you *prove* your code works, to yourself, to your team, and to a client's sceptical IT department. They also let you change code without fear: when the client's export format changes next month, the tests tell you within seconds whether you broke anything.

While the AdmitFlow reference code was being written, a test caught a real bug: importing the same files twice created duplicate records for leads with no contact details. Without that test, it would have reached the counsellors.

## Your first test

```bash
python -m pip install pytest pytest-cov
```

```python
# normalize.py
def normalize_email(value):
    return value.strip().lower()
```

```python
# test_normalize.py
from normalize import normalize_email

def test_strips_and_lowercases():
    assert normalize_email("  Grace@Example.COM ") == "grace@example.com"
```

```bash
pytest
```

pytest finds files named `test_*.py` and functions named `test_*`, runs them, and reports failures with a clear diff of expected versus actual.

## What to test

For each function, think of:
1. **The normal case:** typical input.
2. **Edge cases:** empty string, `None`, very long values, zero, one item.
3. **Real-world mess:** the actual quirks in the client's data (`"Lee, Chloe"`, `"Website "`, `"(202) 555-0141"`, `"Nguyễn"`).
4. **Failure cases:** invalid input should raise the right error.

```python
import pytest
from admitflow.normalize import normalize_source

def test_unknown_source_raises():
    with pytest.raises(ValueError):
        normalize_source("carrier pigeon")
```

## Parametrize: many cases, one test

```python
@pytest.mark.parametrize(
    "raw, expected",
    [
        ("(202) 555-0141", "+12025550141"),
        ("202.555.0141", "+12025550141"),
        ("555-0141", None),
        ("", None),
    ],
)
def test_normalize_phone(raw, expected):
    assert normalize_phone(raw) == expected
```

Each tuple becomes its own test, reported separately.

## Fixtures: shared setup

```python
@pytest.fixture
def store(tmp_path, monkeypatch):
    path = tmp_path / "leads.json"                    # tmp_path: a fresh temporary folder
    monkeypatch.setenv("ADMITFLOW_STORE", str(path))  # set an env var only for this test
    return path

def test_import_creates_store(store):
    main(["import", "--website", "data/leads_sample.csv"])
    assert store.exists()
```

Built-in fixtures you'll use constantly: `tmp_path` (temporary files), `monkeypatch` (env vars and patching), `capsys` (capture printed output).

## Unit, integration and end-to-end

| Level | Tests | Example in AdmitFlow | Speed |
| --- | --- | --- | --- |
| **Unit** | One function in isolation | `test_normalize.py` | Milliseconds |
| **Integration** | Several parts together, real files | `test_importers.py` | Fast |
| **End-to-end** | The whole program as a user runs it | `test_cli.py` runs `main([...])` | Slower |

Write many unit tests, some integration tests, a few end-to-end tests. Module 04 builds on this as the "testing pyramid."

## Coverage

```bash
pytest --cov=admitflow --cov-report=term-missing
```

Coverage shows which lines your tests executed, and lists the ones they missed. Aim for ≥ 80% on your build. But coverage is a floor, not a goal: 100% coverage with weak assertions proves little. **A test should fail if the behaviour is wrong.**

## Arrange, act, assert

```python
def test_same_phone_different_names_is_not_merged():
    # Arrange
    leads = [lead("ENQ-1", 1, "Amara Costa", phone="+12025550174"),
             lead("ENQ-2", 2, "Zara Costa", phone="+12025550174")]
    # Act
    unique, merged = dedupe(leads)
    # Assert
    assert merged == 0
    assert len(unique) == 2
```

Name tests after the **behaviour**, so a failure explains itself.

## Writing tests first (sometimes)

When fixing a bug: **first write a test that reproduces it** and watch it fail, then fix the code and watch it pass. That test now guards against the bug returning. You'll do exactly this in the break & fix.

## Check yourself

Read [`projects/admitflow/tests/test_dedupe.py`](../../../projects/admitflow/tests/test_dedupe.py). Write one more test for a case it doesn't cover: two leads with the same email but different capitalization (`"A@x.com"` vs `"a@x.com"`) after normalization. Does it pass?

Next: [Lesson 13 — Debugging](13-debugging.md)
