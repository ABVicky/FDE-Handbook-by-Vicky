# Lesson 04 — Functions

**Time:** ~4 hours · **Core**

## Why this matters

Functions are how you turn a script into something testable and reusable. In the AdmitFlow reference code, every cleaning rule (`normalize_phone`, `normalize_name`, …) is a small function with its own tests. When the client says "phone numbers from the new kiosk look different," you change one function and its tests, not a 500-line script.

## Defining and calling

```python
def priority(hours_waiting):
    """Return a follow-up priority for a lead."""
    if hours_waiting > 48:
        return "urgent"
    if hours_waiting > 24:
        return "high"
    return "normal"

print(priority(30))   # high
```

- `def` defines; the indented block is the body.
- `return` sends a value back. Without `return`, a function returns `None`.
- The `"""docstring"""` explains what it does. Write one for anything non-obvious.

## Parameters

```python
def greeting(name, course, channel="email"):
    return f"[{channel}] Hi {name}, thanks for your interest in {course}!"

greeting("Grace", "Accounting")                       # default channel
greeting("Omar", "Web Development", channel="sms")   # keyword argument
greeting(course="DA", name="Zoë")                    # any order with keywords
```

### The mutable default trap

```python
def add_note(note, notes=[]):   # ❌ the same list is reused on every call
    notes.append(note)
    return notes

def add_note(note, notes=None): # ✅
    if notes is None:
        notes = []
    notes.append(note)
    return notes
```

## Returning several values

```python
def split_name(full):
    first, _, last = full.partition(" ")
    return first, last          # returns a tuple

first, last = split_name("Grace Patel")
```

## Pure functions are easy to trust

A **pure** function's output depends only on its inputs, and it changes nothing outside itself (no files, no globals, no network).

```python
def normalize_email(value):              # pure: easy to test
    return value.strip().lower()

def save_email(value):                   # not pure: touches a file
    with open("emails.txt", "a") as fh:
        fh.write(normalize_email(value) + "\n")
```

**Design habit:** keep the logic in pure functions; keep reading and writing (I/O) at the edges. You'll see this pattern in `projects/admitflow/admitflow/normalize.py` (pure) versus `store.py` (I/O).

## Scope

Variables created inside a function exist only inside it. Pass values in as parameters and return results; avoid `global`.

## Small functions, good names

If you can't name a function clearly, it's probably doing too much. `clean_and_save_and_email_leads()` should be three functions.

## Check yourself

Write `hours_between(start, end)` that takes two strings like `"2026-09-01 10:00"` and returns the number of hours between them as a float. (Hint: `from datetime import datetime`, `datetime.strptime(s, "%Y-%m-%d %H:%M")`, and subtracting two datetimes gives a `timedelta` with `.total_seconds()`.)

Next: [Lesson 05 — Collections](05-collections.md)
