# Module 03 Build — The AdmitFlow command-line lead manager

**Time:** weeks 3–6, about 20–25 hours in total · **Capabilities:** C2

## Scenario

Your Module 02 shell script answered one question about one file. Now Mr. Fernandes has three exports:

| File | From | Rows |
| --- | --- | --- |
| [`leads_sample.csv`](../../projects/admitflow/data/leads_sample.csv) | Website, phone, walk-ins and WhatsApp, typed up by reception | 120 |
| [`ad_leads.csv`](../../projects/admitflow/data/ad_leads.csv) | The ad platform's lead-form export | 60 |
| [`walkins.csv`](../../projects/admitflow/data/walkins.csv) | Paper forms from an education fair, typed into Excel | 25 |

Many students appear in more than one file. Counsellors are calling the same student twice and missing others. He needs **one clean list**, with no duplicates, that counsellors can search.

The institute's office machines can't install much software, so the tool must run on **plain Python with no third-party packages** (pytest is fine for development).

## Requirements

Build a Python package with a command-line tool called `admitflow`:

### 1. Import and normalize
```bash
admitflow import --website data/leads_sample.csv --ads data/ad_leads.csv --walkins data/walkins.csv
```
- One importer per format, all producing the same `Lead` dataclass
- **Names:** whitespace collapsed, `"Lee, Chloe"` → `"Chloe Lee"`, ALL CAPS fixed, every alphabet preserved (`Nguyễn`, `प्रिया`)
- **Phones:** every format becomes `+12025550141` (E.164 style)
- **Emails:** lower-cased; invalid ones treated as missing
- **Courses:** codes and abbreviations (`DA`, `web_dev`, `BBA`) mapped to official names
- **Dates:** each file's format parsed explicitly (walk-ins are **day first**)
- **Bad rows are reported with a line number and reason, never silently dropped**

### 2. Deduplicate
Agreed rule with the Head of Admissions:
- same email → same person
- same phone **and** same name → same person
- same phone only → **not** merged (families often share one phone)

When merging, keep the earliest enquiry and record every channel the person used.

Importing the same files twice must not create duplicates.

### 3. Store
Save to a JSON file. The location comes from the `ADMITFLOW_STORE` environment variable (default `leads.json`). Writes must not corrupt the file if interrupted (write to a temp file, then rename).

### 4. Use
```bash
admitflow list --source whatsapp --course nursing
```
```bash
admitflow search "nguyễn"
```
```bash
admitflow stats
```
```bash
admitflow export walkins.csv --source walk-in
```
CSV exports must open correctly in Excel, including accented names.

### 5. Quality
- pytest tests for normalization, each importer, dedupe, and the CLI end to end
- **≥ 80% coverage**
- Type hints on all functions
- A README: install, usage, how to run tests, and the dedupe rule
- Built through **at least three pull requests** (suggested: importers → dedupe → CLI)

## Expected results on the sample data

```
data/leads_sample.csv: 120 imported, 0 rejected
data/ad_leads.csv: 60 imported, 0 rejected
data/walkins.csv: 25 imported, 0 rejected
15 duplicate(s) merged; 190 new; 190 unique lead(s) saved to leads.json
```

`admitflow stats` should report **190 unique leads**, **11** who enquired through more than one channel, and **5** with no usable contact details.

Why is "15 merged" bigger than "11 multi-channel"? Work it out from the data. (Hint: look at the `source` column of the website file for the students who also appear in the ad export.)

## Suggested structure

```
my-work/admitflow/
├── pyproject.toml
├── README.md
├── admitflow/
│   ├── __init__.py
│   ├── models.py      # Lead dataclass
│   ├── normalize.py   # pure functions: names, phones, emails, courses
│   ├── importers.py   # one reader per file format
│   ├── dedupe.py
│   ├── store.py       # JSON load/save, CSV export
│   └── cli.py         # argparse commands
└── tests/
```

## Getting started

```bash
cd my-work/admitflow
```

```bash
python3 -m venv .venv && source .venv/bin/activate
```

```bash
python -m pip install --upgrade pip
```

```bash
python -m pip install -e ".[dev]"
```

Start with `normalize.py` and its tests. It's pure functions, so it's the easiest place to begin, and everything else depends on it.

## Done when

- [ ] The sample import gives exactly the expected results above
- [ ] Re-running the import changes nothing
- [ ] `admitflow search "nguyễn"` finds the Nguyễn leads; `search "प्रिया"` finds प्रिया शर्मा
- [ ] Siblings sharing a phone number (Amara Costa and Zara Costa style) are **not** merged; write a test for it
- [ ] `pytest` passes with ≥ 80% coverage
- [ ] Merged via ≥ 3 reviewed pull requests
- [ ] README written

## Stretch

- `admitflow import --dry-run` shows what would change without saving
- A `--since 2026-09-15` filter on `list` and `export`
- A report of possible duplicates the rules didn't merge (same phone, *similar* name) for a human to review
- Time the import on 100,000 generated leads. Is it still fast? (Lesson 16)

## Reference solution

[`projects/admitflow/`](../../projects/admitflow/README.md). Compare **after** you finish. Reading it is also good practice for [Lesson 13's](lessons/13-debugging.md) "reading unfamiliar code" routine.
