# Lesson 02 — Values, variables and types

**Time:** ~3 hours · **Core**

## Variables are names for values

```python
course = "Data Analytics"
seats = 30
fee = 1250.50
is_open = True
counsellor = None   # "no value yet"
```

A variable is a label attached to a value. You can move the label: `seats = seats - 1`.

Naming: `lower_case_with_underscores`, descriptive (`enquiries_this_week`, not `x`).

## The basic types

| Type | Example | Notes |
| --- | --- | --- |
| `int` | `30`, `-4` | Whole numbers, any size |
| `float` | `1250.5` | Decimals, but **inexact**: `0.1 + 0.2 == 0.3` is `False` |
| `str` | `"Zoë"` | Text (Lesson 06) |
| `bool` | `True`, `False` | |
| `None` | `None` | Absence of a value |

```python
type(30)        # <class 'int'>
type("30")      # <class 'str'>: "30" is text, not a number
```

**Money tip:** never store money as `float` in real systems. Use whole cents (`125050`) or `decimal.Decimal("1250.50")`.

## Converting between types

Data from files, forms and APIs often arrives as **strings**. Convert deliberately:

```python
int("30")          # 30
float("1250.50")   # 1250.5
str(30)            # "30"
int("thirty")      # ValueError: you must handle this (Lesson 08)
bool("")           # False: empty values are "falsy"
bool("no")         # True: any non-empty string is "truthy"!
```

That last line catches people out: a CSV value `"no"` or `"False"` is still truthy.

## Operators

```python
7 + 2, 7 - 2, 7 * 2   # 9, 5, 14
7 / 2                 # 3.5: always a float
7 // 2                # 3: whole-number division
7 % 2                 # 1: remainder
2 ** 10               # 1024: power

seats == 30, seats != 30, seats >= 10   # comparisons give bool
is_open and seats > 0
not is_open
```

Checking for `None`: use `is`, not `==`:

```python
if counsellor is None:
    print("unassigned")
```

## f-strings: building text

```python
name, count = "Priya", 12
print(f"{name} has {count} follow-ups today")
print(f"Conversion: {0.0912:.1%}")      # Conversion: 9.1%
print(f"{'Course':<20}|")              # left-align to width 20
```

## Check yourself

Predict, then run in the REPL:
```python
a = "5"
b = 3
print(a * b)
print(int(a) * b)
print(0.1 + 0.2)
print(bool("False"))
```

Next: [Lesson 03 — Control flow](03-control-flow.md)
