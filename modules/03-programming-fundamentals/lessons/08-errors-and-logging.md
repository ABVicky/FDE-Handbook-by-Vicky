# Lesson 08 — Errors, exceptions and logging

**Time:** ~3 hours · **Core**

## Why this matters

Client data *will* contain things your code doesn't expect. What matters is what happens next. A silent failure that loses records can go unnoticed for months. A loud, clear failure gets fixed in minutes. This lesson is about making failures loud, clear and safe.

## Reading a traceback

```
Traceback (most recent call last):
  File "import.py", line 12, in <module>
    received = parse_date(row["received_at"])
  File "import.py", line 5, in parse_date
    return datetime.strptime(value, "%Y-%m-%d %H:%M")
ValueError: time data '04/09/2026' does not match format '%Y-%m-%d %H:%M'
```

Read it **bottom-up**: the last line is *what* went wrong; the lines above show *where*, ending with the line that failed.

## Handling exceptions

```python
def parse_seats(value):
    try:
        return int(value)
    except ValueError:
        return None
```

The full shape:

```python
try:
    result = risky()
except (ValueError, KeyError) as exc:   # specific, expected problems
    handle(exc)
else:
    pass                                 # runs only if no exception
finally:
    pass                                 # always runs (cleanup)
```

### The most important rule

```python
try:
    lead = parse(row)
except Exception:      # ❌ catches EVERYTHING: typos, renamed columns, bugs
    continue           # ❌ and hides it
```

Catch only the exceptions you **expect and can handle**, and record what you rejected:

```python
rejected = []
try:
    lead = parse(row)
except ValueError as exc:                 # ✅ specific
    rejected.append((line_num, str(exc))) # ✅ visible
```

Anything unexpected should crash. A crash is a bug report; silence is data loss.

## Raising your own exceptions

```python
def normalize_source(value):
    source = value.strip().lower()
    if source not in {"website", "ad", "phone", "walk-in", "whatsapp"}:
        raise ValueError(f"unknown source: {value!r}")
    return source
```

`{value!r}` shows the value with quotes, so `'website '` (with a trailing space) is visible in the message.

## Logging instead of print

`print` is for output the user asked for. **Logging** is for diagnostic messages, with levels you can turn up or down:

```python
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
log = logging.getLogger("admitflow.import")

log.debug("row parsed: %s", row)              # very detailed, usually hidden
log.info("imported %d leads", 120)            # normal progress
log.warning("line %d rejected: %s", 7, exc)   # something unusual, still running
log.error("could not read %s", path)          # an operation failed
```

Pass values as arguments (`"%d leads", 120`) rather than f-strings. The logging system only formats them if the message is actually shown.

Logging levels let the same code be quiet for counsellors and detailed when you're debugging on a client's server, without editing the code.

**Never log secrets or unnecessary personal data** (passwords, API keys, full phone numbers in bulk). Module 10 covers this properly.

## Checklist for data-processing code

- [ ] Counts in = counts out + counts rejected
- [ ] Every rejection has a line number and a reason
- [ ] Only expected exceptions are caught
- [ ] A non-zero exit code when something needs human attention

## Check yourself

Rewrite this so no row can disappear silently:
```python
results = []
for row in rows:
    try:
        results.append(int(row["seats"]))
    except:
        pass
```

Next: [Lesson 09 — Modules, packages and dependencies](09-modules-and-packages.md)
