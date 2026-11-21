# Lesson 05 — Collections: lists, dicts, sets, tuples

**Time:** ~5 hours · **Core**

## Why this matters

Real data is collections: rows of leads, maps from IDs to records, sets of emails already seen. Choosing the right collection makes code simpler *and* faster.

## The four collections

| Type | Literal | Ordered? | Changeable? | Duplicates? | Use for |
| --- | --- | --- | --- | --- | --- |
| `list` | `["a", "b"]` | Yes | Yes | Yes | Sequences of items |
| `tuple` | `("a", "b")` | Yes | No | Yes | Fixed groups of values (a row, a coordinate) |
| `dict` | `{"id": 1}` | Yes (insertion order) | Yes | Keys unique | Lookup by key; records |
| `set` | `{"a", "b"}` | No | Yes | No | Membership tests; removing duplicates |

## Lists

```python
sources = ["website", "ad"]
sources.append("phone")
sources[0]          # "website"
sources[-1]         # "phone": counting from the end
sources[1:3]        # ["ad", "phone"]: slicing
len(sources)        # 3
"ad" in sources     # True
sorted(["b", "a"])  # ["a", "b"]: returns a new list
```

## Dictionaries

A dict maps **keys** to **values**: perfect for a record or a lookup table.

```python
lead = {"id": "ENQ-0001", "name": "Grace Patel", "course": "Accounting"}
lead["name"]                 # "Grace Patel"
lead.get("phone")            # None: no KeyError
lead.get("phone", "unknown") # "unknown"
lead["phone"] = "+12025550141"

for key, value in lead.items():
    print(key, "=", value)
```

Lookup tables replace long `if/elif` chains:

```python
COURSES = {"da": "Data Analytics", "bba": "Business Administration"}
COURSES.get("da", "Unknown")   # "Data Analytics"
```

## Sets

```python
seen = set()
for email in ["a@x.com", "b@x.com", "a@x.com"]:
    if email in seen:
        print("duplicate:", email)
    seen.add(email)

{"website", "ad"} | {"ad", "phone"}   # union: {'website', 'ad', 'phone'}
{"website", "ad"} & {"ad", "phone"}   # intersection: {'ad'}
```

Checking `x in some_set` is fast no matter how big the set is; `x in some_list` checks every item (Lesson 16).

## Tuples and unpacking

```python
row = ("ENQ-0001", "Grace Patel", "Accounting")
lead_id, name, course = row
```

Tuples can be dict keys (lists can't). The AdmitFlow dedupe uses `(phone, name)` tuples as keys.

## Comprehensions

A compact way to build a collection from another:

```python
waits = [2, 30, 5, 49]
late = [h for h in waits if h > 24]                 # [30, 49]
squares = {h: h * h for h in waits}                 # dict
domains = {e.split("@")[1] for e in ["a@x.com", "b@y.org", "c@x.com"]}   # {'x.com', 'y.org'}
total_late = sum(1 for h in waits if h > 24)        # 2
```

If a comprehension needs more than one `if` or doesn't fit on a line, write a normal loop.

## Two very useful tools

```python
from collections import Counter, defaultdict

Counter(["ad", "website", "ad"]).most_common()   # [('ad', 2), ('website', 1)]

by_course = defaultdict(list)
for name, course in [("Grace", "Accounting"), ("Omar", "Accounting")]:
    by_course[course].append(name)
# {'Accounting': ['Grace', 'Omar']}
```

## A list of dicts: the shape of most data

```python
leads = [
    {"name": "Grace", "source": "website", "hours": 30},
    {"name": "Omar", "source": "ad", "hours": 2},
]
late_names = [lead["name"] for lead in leads if lead["hours"] > 24]
leads_by_wait = sorted(leads, key=lambda lead: lead["hours"], reverse=True)
```

## Check yourself

Given `leads` (a list of dicts with `"email"` and `"source"`), write code that prints the number of **unique** emails per source. Which collection(s) did you use, and why?

Next: [Lesson 06 — Strings, text and Unicode](06-strings-and-unicode.md)
