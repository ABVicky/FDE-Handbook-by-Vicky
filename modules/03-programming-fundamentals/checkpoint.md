# Module 03 — Checkpoint

Pass mark: **10 / 12**, plus the [build](build.md) and [break & fix](break-and-fix/README.md), to skip this module. Answer without running the code first, then check by running it.

---

**1.** What does this print?
```python
leads = ["Grace", "Omar", "Zoë"]
for i, name in enumerate(leads, start=1):
    if name.startswith("O"):
        continue
    print(i, name)
```

**2.** What's wrong with this function, and how do you fix it?
```python
def add_note(note, notes=[]):
    notes.append(note)
    return notes
```

**3.** Write a dictionary comprehension that maps each course name to its length, for `courses = ["Accounting", "Web Development"]`.

**4.** Which data structure would you use to check, thousands of times, whether an email address has already been seen? Why?
- a) list  b) tuple  c) set  d) string

**5.** Why does `"José" == "José"` sometimes return `False`, even though both look identical? What function fixes it?

**6.** What's the problem with reading a CSV like this?
```python
for line in open("leads.csv"):
    name, phone, email = line.split(",")
```

**7.** What's wrong here, and what should it be?
```python
try:
    lead = parse(row)
except Exception:
    pass
```

**8.** What is a virtual environment, and why should every project have its own?

**9.** What does this test check, and will it pass?
```python
def normalize_email(s):
    return s.strip().lower()

def test_normalize_email():
    assert normalize_email("  Grace@Example.COM ") == "grace@example.com"
```

**10.** You call an API and get `429 Too Many Requests`. What should your code do?

**11.** In Git, what's the difference between `git commit` and `git push`?

**12.** What does this JavaScript print, and why?
```javascript
async function getCount() { return 42; }
const result = getCount();
console.log(result);
```

---

<details>
<summary><strong>Answers</strong></summary>

1. `1 Grace` then `3 Zoë`. `continue` skips Omar, but `enumerate` still counts him.
2. The default list is created **once**, when the function is defined, so it's shared between calls and notes pile up. Use `notes=None`, then `if notes is None: notes = []`.
3. `{course: len(course) for course in courses}` → `{"Accounting": 10, "Web Development": 15}`
4. **c) set**: membership checks are on average constant time (O(1)); a list is O(n).
5. Unicode allows `é` as one character or as `e` + a combining accent. `unicodedata.normalize("NFC", s)` makes them identical.
6. It breaks on quoted fields containing commas (`"Lee, Chloe"`), on extra or missing columns, and it keeps the newline on the last field. Use the `csv` module (`csv.DictReader`).
7. It silently swallows *every* error, including bugs you didn't predict, which leads to silent data loss. Catch only the specific exceptions you expect (e.g. `ValueError`), and record or log what was rejected.
8. An isolated folder with its own Python packages. Projects need different package versions; without isolation, installing for one project can break another, and you can't reproduce the setup on a client's machine.
9. It checks that whitespace is stripped and the email is lower-cased. It **passes**.
10. Wait and retry, ideally respecting the `Retry-After` header, with exponential backoff and a maximum number of attempts. Don't retry immediately in a tight loop.
11. `commit` records a snapshot in your **local** repository. `push` sends your commits to the **remote** (e.g. GitHub).
12. `Promise { 42 }`. An `async` function always returns a Promise. You need `await getCount()` (inside an async function) or `.then()` to get `42`.

</details>
