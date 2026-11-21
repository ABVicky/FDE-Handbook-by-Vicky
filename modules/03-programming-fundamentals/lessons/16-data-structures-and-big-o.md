# Lesson 16 — Data structures and Big-O

**Time:** ~4 hours · **Core**

## Why this matters

Code that's instant on a 200-row sample can take hours on the client's 2 million rows. Big-O is a quick way to predict that *before* it happens. It's also a staple of coding interviews (Module 12).

## Big-O in one idea

Big-O describes **how the work grows as the input grows**, ignoring constant details.

| Big-O | Name | Example | 1,000 items | 1,000,000 items |
| --- | --- | --- | --- | --- |
| O(1) | Constant | `email in seen_set`, `d[key]` | 1 step | 1 step |
| O(log n) | Logarithmic | Binary search in a sorted list | ~10 | ~20 |
| O(n) | Linear | One loop over the data | 1,000 | 1,000,000 |
| O(n log n) | | Sorting | ~10,000 | ~20,000,000 |
| O(n²) | Quadratic | Loop inside a loop over the same data | 1,000,000 | 1,000,000,000,000 😱 |

## The classic FDE performance bug

Deduplicating by comparing every lead with every other lead:

```python
# O(n²): fine for 200 leads, hopeless for 2 million
duplicates = []
for i, a in enumerate(leads):
    for b in leads[i + 1:]:
        if a["email"] == b["email"]:
            duplicates.append((a, b))
```

Using a dict as an index:

```python
# O(n): one pass
first_seen = {}
duplicates = []
for lead in leads:
    key = lead["email"]
    if key in first_seen:
        duplicates.append((first_seen[key], lead))
    else:
        first_seen[key] = lead
```

This is exactly how [`dedupe.py`](../../../projects/admitflow/admitflow/dedupe.py) works: dicts keyed by email and by `(phone, name)`.

Similarly, `if email in some_list` inside a loop is O(n²) overall. Convert the list to a set first.

## Python's built-in structures, by cost

| Operation | list | dict / set |
| --- | --- | --- |
| Look up by position `x[i]` | O(1) | n/a |
| Is `x` in it? | **O(n)** | **O(1)** average |
| Add to the end / add a key | O(1) | O(1) |
| Insert/remove at the front | O(n) | n/a |
| Sort | O(n log n) | n/a |

Need a fast queue (add at one end, remove at the other)? `collections.deque`. Need the smallest item repeatedly (e.g. next follow-up due)? `heapq`.

## Other structures worth knowing

| Structure | What it is | Where it shows up |
| --- | --- | --- |
| **Stack** (last in, first out) | `list` with `append`/`pop` | Undo, parsing, depth-first search |
| **Queue** (first in, first out) | `deque` | Job queues, breadth-first search |
| **Heap** | `heapq` | Priority queues, scheduling |
| **Tree** | Nested nodes | File systems, JSON, database indexes |
| **Graph** | Nodes and edges | Org charts, dependency maps, networks |

## Measuring instead of guessing

```python
import time
start = time.perf_counter()
run_import()
print(f"{time.perf_counter() - start:.2f}s")
```

Test with **realistic volume**: generate 100,000 fake leads and time your code. If doubling the input quadruples the time, look for a nested loop.

## Interview practice

Many FDE interviews include data-structure problems. Practise on a platform such as LeetCode or HackerRank. Start with "easy" problems on arrays, strings and hash maps (dicts/sets), which are the most relevant to real FDE work. Aim to explain your solution's Big-O out loud.

## Check yourself

1. What's the Big-O of this, and how would you make it O(n)?
   ```python
   unsubscribed = [...]   # a list of 50,000 emails
   to_contact = [l for l in leads if l["email"] not in unsubscribed]
   ```
2. You need the 10 most overdue follow-ups from 1 million. Sorting all of them is O(n log n). What's a faster approach?

Next: [Lesson 17 — Git and GitHub](17-git-and-github.md)
