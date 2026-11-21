# Break & Fix — Solution

> ⚠️ Try it properly first.

## Reproduce

```bash
python3 clean_ad_leads.py ../../../projects/admitflow/data/ad_leads.csv cleaned.csv
```

The input has 60 leads; `cleaned.csv` has **31**. **29 students (48%)** were silently dropped, every week.

## Root cause: two bugs working together

| # | Bug | Effect |
| --- | --- | --- |
| 1 | `VALID_NAME = re.compile(r"^[A-Za-z][A-Za-z .'-]*$")` | `[A-Za-z]` means *only the 52 unaccented English letters*. José, Zoë, Nguyễn, Søndergaard, Łucja and प्रिया are all "invalid". |
| 2 | `except Exception: continue` | Every rejected row, **and any other error at all**, vanishes without a trace. The script says "Done." no matter what. |

Bug 1 caused the damage. Bug 2 hid it for months. Bug 2 is the more serious one: it would hide the *next* bug too.

## The fix

[`solution/clean_ad_leads.py`](solution/clean_ad_leads.py) changes three things:

1. **Validate letters in any script:** `any(ch.isalpha() for ch in name)`. Python's `str.isalpha()` understands Unicode. (Also normalizes to NFC, so `é` typed two different ways compares equal.)
2. **Catch only what you expect:** `except ValueError as exc:`. Anything unexpected (a renamed column, a corrupt file) now crashes loudly, which is what you want.
3. **Report every rejected row** with its line number, print a summary (`Read 60 rows: wrote 60…, rejected 0`), and **exit non-zero** if anything was rejected, so a scheduled job or a human notices.

Regression tests: [`solution/test_clean_ad_leads.py`](solution/test_clean_ad_leads.py)

```bash
cd solution && python3 -m pytest test_clean_ad_leads.py
```

## Sample incident note

> **Subject: Ad enquiries missing from the weekly counsellor list (fixed)**
> The script that cleans the ad-platform export was rejecting any name with letters outside basic English (accents, other alphabets) and hiding those rejections. In this month's export, 29 of 60 enquiries (48%) were dropped, including José Chen and Zoë García. It has been fixed and tested; all 60 now come through, and any future rejected row is reported by line.
> **Next steps:** (1) we'll re-run all past exports so counsellors can contact the missed students this week; (2) please let me know if older exports are available; (3) we'll replace this script with the AdmitFlow importer, which already handles these names.

## Lessons for an FDE

- **"No errors" isn't the same as "working."** Always check counts: rows in versus rows out.
- **Never `except Exception: pass/continue`** in data code. It turns bugs into silent data loss.
- **Real people's names don't fit your assumptions.** Search "falsehoods programmers believe about names". Your validation should be as permissive as possible.
- **The business impact is the headline.** "48% of ad leads never reached counsellors" is what the client needs to hear, and it's also why this matters to the ad budget (Ms. Rao's main question in Module 01).
