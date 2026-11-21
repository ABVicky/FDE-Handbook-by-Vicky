# Lesson 09 — Modules, packages and dependencies

**Time:** ~3 hours · **Core**

## Modules: one file, one job

Any `.py` file is a **module**. Split code by responsibility and import what you need:

```python
# normalize.py
def normalize_email(value):
    return value.strip().lower()
```

```python
# main.py
from normalize import normalize_email
import normalize            # or import the whole module

print(normalize_email(" A@B.com "))
print(normalize.normalize_email(" A@B.com "))
```

## Packages: a folder of modules

```
projects/admitflow/
├── pyproject.toml        ← project metadata and dependencies
├── admitflow/            ← the package
│   ├── __init__.py       ← marks the folder as a package
│   ├── models.py
│   ├── normalize.py
│   ├── importers.py
│   ├── dedupe.py
│   ├── store.py
│   └── cli.py
└── tests/
```

Inside a package, modules import each other **relatively**:

```python
# admitflow/importers.py
from .models import Lead
from .normalize import normalize_phone
```

## `if __name__ == "__main__":`

```python
def main():
    print("running")

if __name__ == "__main__":
    main()
```

The block runs only when the file is executed directly (`python3 tool.py`), not when it's imported. That keeps imports free of side effects, and keeps functions testable.

## The standard library

Python ships with a lot. Check here before installing anything: `csv`, `json`, `pathlib`, `datetime`, `re`, `logging`, `argparse` (command-line arguments), `collections`, `unicodedata`, `urllib`, `sqlite3`, `unittest`… The AdmitFlow CLI uses **only** the standard library, which makes it easy to run on a locked-down client machine.

## Third-party packages

Installed from [PyPI](https://pypi.org/) with pip, inside your venv:

```bash
python -m pip install httpx
```

Record your dependencies so anyone can recreate the environment. The modern way is `pyproject.toml`:

```toml
[project]
name = "admitflow"
version = "0.3.0"
requires-python = ">=3.9"
dependencies = []                       # what the app needs to run

[project.optional-dependencies]
dev = ["pytest>=8", "pytest-cov>=5"]    # extra tools for developers

[project.scripts]
admitflow = "admitflow.cli:main"        # creates an `admitflow` command
```

Install the project itself, in **editable** mode (code changes take effect without reinstalling), with dev tools:

```bash
python -m pip install -e ".[dev]"
```

You'll also see the older `requirements.txt` (one package per line, often with exact versions: `httpx==0.27.2`). `pip freeze > requirements.txt` captures what's installed.

## Choosing dependencies (an FDE concern)

Every dependency is code you're trusting, and will have to maintain on the client's systems. Before adding one, ask:
- Does the standard library already do this?
- Is it actively maintained? Widely used?
- What's its licence? Is it compatible with the client's rules?
- Will the client's security team allow it? (Some organizations only allow approved packages from an internal mirror.)

**Pin versions** for anything deployed, so a new release can't break production without you noticing.

## Check yourself

1. Why does `from .models import Lead` work inside `admitflow/importers.py` but fail if you run `python3 importers.py` directly?
2. What does `pip install -e ".[dev]"` install?

Next: [Lesson 10 — Classes and dataclasses](10-classes-and-dataclasses.md)
