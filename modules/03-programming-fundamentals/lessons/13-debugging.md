# Lesson 13 — Debugging

**Time:** ~3 hours · **Core**

## Why this matters

FDEs debug code they didn't write, on systems they don't control, under time pressure. The method from [Module 02, Lesson 07](../../02-computing-foundations/lessons/07-troubleshooting.md) still applies: reproduce, read, hypothesize, test one thing. This lesson adds Python's tools.

## Step 0: shrink the problem

Before using any tool, find the **smallest input that still fails**. If 1 row out of 10,000 crashes the import, copy that row into a tiny test file. Most bugs become obvious once the problem is small.

## print debugging (fine, but temporary)

```python
print(f"DEBUG row={row!r}")
```

`!r` shows exact values, including invisible spaces and `\r`. Remove debug prints before committing. Use `logging.debug` for anything worth keeping.

## The debugger: `breakpoint()`

Put `breakpoint()` where you want to stop:

```python
for line_num, row in rows:
    if row["enquiry_id"] == "ENQ-0042":
        breakpoint()
    lead = parse(row)
```

Run the program; it pauses there with a `(Pdb)` prompt:

| Command | Does |
| --- | --- |
| `p row` | Print a variable |
| `pp row` | Pretty-print it |
| `n` | Next line (step over) |
| `s` | Step into a function call |
| `c` | Continue until the next breakpoint |
| `l` | Show code around the current line |
| `w` | Where am I? (call stack) |
| `q` | Quit |

## The VS Code debugger

Click left of a line number to set a red breakpoint dot, then press <kbd>F5</kbd> and choose *Python File*. You can hover over variables, watch expressions, and step through code. For tests: the Testing panel lets you debug a single failing test.

## Debugging a failing test

```bash
pytest -x -k phone -vv
```

- `-x` stops at the first failure
- `-k phone` runs only tests with "phone" in the name
- `-vv` shows full details
- `--pdb` opens the debugger at the point of failure

## Reading unfamiliar code

A routine for code you've never seen:
1. **Find the entry point:** `main()`, `if __name__ == "__main__"`, or the `[project.scripts]` entry.
2. **Follow one real input** through the code, end to end. Don't try to read everything.
3. **Draw it:** boxes for modules, arrows for calls.
4. **Run the tests** to see what the author thought was important.
5. **Change something small** and see what breaks.
6. **Write down** what you learned in a short README section for the next person.

Practise on [`projects/admitflow/admitflow/cli.py`](../../../projects/admitflow/admitflow/cli.py): trace what happens when someone runs `admitflow import --ads data/ad_leads.csv`.

## Common Python bugs

| Symptom | Common cause |
| --- | --- |
| `KeyError: 'Date'` but the column exists | BOM in the header (`'﻿Date'`): use `encoding="utf-8-sig"` |
| `TypeError: unsupported operand type(s) for +: 'int' and 'str'` | A number read from a file is still a string |
| `AttributeError: 'NoneType' object has no attribute 'lower'` | A function returned `None` (missing `return`?) or the value is missing |
| Values "leak" between function calls | Mutable default argument |
| Comparison unexpectedly `False` | Trailing whitespace, case, or Unicode normalization |
| Fewer rows out than in, no errors | A broad `except` hiding failures |

## Check yourself

Put a `breakpoint()` in `normalize_name` in the AdmitFlow code, run `admitflow import --walkins data/walkins.csv`, and step through how `"  LUCÍA  FERNÁNDEZ "` becomes `"Lucía Fernández"`. Write down each intermediate value.

Next: [Lesson 14 — Calling HTTP APIs](14-calling-http-apis.md)
