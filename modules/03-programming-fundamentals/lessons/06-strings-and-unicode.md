# Lesson 06 — Strings, text and Unicode

**Time:** ~4 hours · **Core**

## Why this matters

Names, emails, addresses, notes, documents, LLM prompts: FDE work is full of text, and real text is messy. It has extra spaces, inconsistent capitals, and characters from every language. Mishandling it doesn't usually crash your program. It silently produces wrong results, as you'll see in this module's break & fix.

## Everyday string methods

```python
raw = "  Grace.PATEL@Example.com \n"
raw.strip()                    # remove surrounding whitespace
raw.strip().lower()            # "grace.patel@example.com"
"grace patel".title()          # "Grace Patel"
"a,b,c".split(",")             # ["a", "b", "c"]
" ".join(["Grace", "Patel"])   # "Grace Patel"
"  too   many  spaces ".split()  # ["too", "many", "spaces"]: split() with no argument splits on any whitespace
"Walk-in".replace("-", " ")    # "Walk in"
"ENQ-0001".startswith("ENQ")   # True
"Patel, Grace".partition(",")  # ("Patel", ",", " Grace")
```

Strings are **immutable**: methods return a *new* string; the original doesn't change.

Collapsing whitespace is a classic one-liner:

```python
" ".join("  Lucía   Fernández ".split())   # "Lucía Fernández"
```

## Searching and checking

```python
"nurs" in "Nursing Assistance".lower()   # True
"Zoë".isalpha()      # True: isalpha understands Unicode letters
"2025550141".isdigit()
"ENQ-0001".find("-") # 3 (or -1 if not found)
```

## Regular expressions (a little goes a long way)

```python
import re
re.sub(r"\D", "", "(202) 555-0141")    # "2025550141": remove non-digits
re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", "a@b.com") is not None   # rough email check
```

Be careful: `[A-Za-z]` matches **only** unaccented English letters. That one pattern is the root cause of this module's break & fix.

## Unicode: text is more than English

Every character is a Unicode **code point**: `A` is U+0041, `é` is U+00E9, `प` is U+092A. Python 3 strings are Unicode by default, so `"प्रिया"` just works.

Three things you must know:

**1. Files have encodings.** On disk, text is stored as bytes using an **encoding**. Use **UTF-8** everywhere, and say so explicitly:

```python
open("leads.csv", encoding="utf-8")
```

Files exported from Excel often start with an invisible **BOM** (byte-order mark). Read them with `encoding="utf-8-sig"` or your first column header becomes `"﻿Date"` instead of `"Date"`.

**2. The same text can have different code points.** `é` can be one code point (U+00E9) or `e` + a combining accent (U+0065 U+0301). They look identical but don't compare equal:

```python
import unicodedata
a, b = "José", "José"
a == b                                                              # False!
unicodedata.normalize("NFC", a) == unicodedata.normalize("NFC", b)  # True
```

Normalize (NFC) any text you'll compare or use as a key.

**3. Case-insensitive comparison: use `casefold()`.** It handles more languages correctly than `lower()`:

```python
"STRASSE".casefold() == "straße".casefold()   # True
```

## Respect people's names

Names may have accents, apostrophes, hyphens, several parts, one part, or a non-Latin script. Some cultures put the family name first. Good rules for FDE systems:
- Don't "validate" names beyond "has at least one letter."
- Don't force capitalization unless the input is clearly ALL CAPS or all lower-case.
- Store what the person wrote; normalize a *separate* key for matching.

## Check yourself

Write `clean_name(raw)` that: collapses whitespace, converts `"Lee, Chloe"` to `"Chloe Lee"`, title-cases only ALL-CAPS or all-lower input, and keeps `"Nguyễn Thu"` and `"प्रिया शर्मा"` unchanged. Compare with `normalize_name` in [`projects/admitflow/admitflow/normalize.py`](../../../projects/admitflow/admitflow/normalize.py).

Next: [Lesson 07 — Files, CSV and JSON](07-files-csv-json.md)
