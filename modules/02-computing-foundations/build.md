# Module 02 Build — Count leads by channel from the terminal

**Time:** 2–3 hours · **Capabilities:** C2, C4

## Scenario

Before investing in any new system, Mr. Fernandes (Head of Admissions) wants a quick answer: **"How many enquiries did we get from each channel last month?"** The IT administrator has exported last month's leads into one file: [`projects/admitflow/data/leads_sample.csv`](../../projects/admitflow/data/leads_sample.csv).

You're on the institute's office computer: no Python libraries installed, no spreadsheet licence. Just a terminal. Write a **reusable shell script**.

## Requirements

Create `my-work/admitflow/m02/count_by_source.sh` that:

1. Takes the CSV file path as its **first argument**:
   ```bash
   ./count_by_source.sh projects/admitflow/data/leads_sample.csv
   ```
2. Prints a count per source, **highest first**, plus a total:
   ```
   website   52
   ad        34
   ...
   TOTAL     120
   ```
3. **Handles messy data:**
   - Ignores the header line and blank lines
   - Treats `Website`, `website` and `Website ` (trailing space) as the same channel
   - Isn't fooled by names like `"Rao, Anita"` that contain a comma
   - Copes with Windows line endings (`\r\n`) if the file was edited on Windows
4. **Fails helpfully:**
   - No argument → prints `usage: count_by_source.sh FILE` and exits with a non-zero code
   - File doesn't exist → prints a clear error and exits non-zero
5. Starts with a shebang and `set -euo pipefail`, and is executable.

## Test it

```bash
./count_by_source.sh projects/admitflow/data/leads_sample.csv
```

```bash
./count_by_source.sh; echo "exit code: $?"
```

```bash
./count_by_source.sh nope.csv; echo "exit code: $?"
```

Test Windows line endings by making a converted copy:

```bash
sed 's/$/\r/' projects/admitflow/data/leads_sample.csv > /tmp/leads_crlf.csv
```

```bash
./count_by_source.sh /tmp/leads_crlf.csv
```

Both runs must print the same counts.

## Done when

- [ ] The TOTAL is **120**, and it equals the sum of the channel counts
- [ ] There are exactly **5** channels (no duplicates caused by case or spaces)
- [ ] The CRLF copy gives identical output
- [ ] Missing argument and missing file both exit non-zero with a clear message
- [ ] You wrote a 3-line note for Mr. Fernandes: the numbers, one data-quality issue you noticed, and one question it raises

## Stretch

- Add an optional second argument for a date prefix, e.g. `2026-09-1` to count only 10th–19th September.
- Print percentages next to the counts.

Reference: [build-solution.md](build-solution.md). Try it yourself first.
