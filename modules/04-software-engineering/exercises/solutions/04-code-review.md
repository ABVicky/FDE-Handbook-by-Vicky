# Exercise 04 — Model review

**Overall: Request changes.** The idea is useful, but this endpoint exposes every student's contact details to anyone on the internet.

| # | Severity | Issue | Why it matters | Suggested fix |
| --- | --- | --- | --- | --- |
| 1 | 🔴 Critical | **No authentication**: no `current_user` dependency | Anyone who finds `/export` downloads all names, phones and emails, which is a data-protection breach | Add `Depends(require_admin)` (the director/admin only), plus a test that it returns `401`/`403` |
| 2 | 🔴 High | **Personal data printed to stdout** (`print("exported", rows)`) | Logs are kept, copied and shared; now they contain every student's contact details | Remove it. If needed, log `exported %d leads` with the count only |
| 3 | 🟠 High | **Hand-built CSV** | Names like `"Lee, Chloe"` or with quotes break the columns; values starting with `=`, `+`, `-`, `@` can execute as formulas in Excel (CSV injection) | Use `csv.writer` (or the existing `store.export_csv`), and prefix risky leading characters with `'` |
| 4 | 🟠 Medium | **Silently truncated to 100 leads** (`limit=100`) | The director gets a partial file and thinks it's complete | Export everything (stream it if large), or paginate explicitly and say so |
| 5 | 🟡 Medium | `None` written as the text `None` | Spreadsheet shows "None" for missing phones | Write empty strings for missing values |
| 6 | 🟡 Medium | No `Content-Disposition` header; not UTF-8 BOM | Browser may display rather than download; Excel garbles `Nguyễn` | `Content-Disposition: attachment; filename="leads.csv"`, encode `utf-8-sig` |
| 7 | 🟡 Low | String concatenation in a loop | Quadratic-ish for big exports | `csv.writer` into `io.StringIO`, or a `StreamingResponse` |
| 8 | ⚪ Process | No tests, vague description | Reviewers can't tell what was checked | Tests for auth, quoting, full export; description with what/why/how tested |

**Comment to the author (tone matters):**
> Thanks, the director will love this. Before merging, could we lock it to admins and drop the `print`? Right now it would expose all student contacts publicly. I'd also suggest reusing `store.export_csv`, which already handles quoting and Excel encoding. Happy to pair on the tests if useful.
