# Module 02 Build — Reference Solution

> ⚠️ Finish your own script first.

The script: [`solution/count_by_source.sh`](solution/count_by_source.sh)

```bash
#!/usr/bin/env bash
# count_by_source.sh — count AdmitFlow leads per channel (Module 02 reference solution)
# Usage: count_by_source.sh FILE
set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "usage: count_by_source.sh FILE" >&2
  exit 2
fi

file="$1"
if [[ ! -f "$file" ]]; then
  echo "error: file not found: $file" >&2
  exit 1
fi

tail -n +2 "$file" \
  | tr -d '\r' \
  | awk -F, 'NF {
      s = tolower($NF)
      gsub(/^[ \t]+|[ \t]+$/, "", s)
      count[s]++
      total++
    }
    END {
      for (s in count) printf "%-10s %d\n", s, count[s] | "sort -k2,2nr"
      close("sort -k2,2nr")
      printf "%-10s %d\n", "TOTAL", total
    }'
```

## Output

```
website    52
ad         34
phone      12
walk-in    11
whatsapp   11
TOTAL      120
```

(`walk-in` and `whatsapp` tie at 11, so their order may differ on your machine.)

## Why each piece is there

| Piece | Handles |
| --- | --- |
| `$# -lt 1` check, `exit 2` | Missing argument → usage message, non-zero exit |
| `-f "$file"` check | Missing file → clear error instead of a confusing `tail` message |
| `>&2` | Errors go to *stderr*, so they don't mix with real output if someone pipes it |
| `tail -n +2` | Skips the header |
| `tr -d '\r'` | Windows line endings |
| `NF` in awk | Skips blank lines (zero fields) |
| `$NF` (last field) | Source is the last column, so commas in quoted names earlier in the line don't matter |
| `tolower` + `gsub` | `Website`, `website`, `Website ` all become `website` |
| `total++` | Total computed from the same rows, so it always equals the sum |

## A good note for Mr. Fernandes

> Last month we received **120 enquiries**: website 52 (43%), ads 34 (28%), phone 12, walk-in 11, WhatsApp 11.
> Data quality: channel names are typed inconsistently ("Website", "website ", "Walk-in" vs "walk-in"), and 15 enquiries have no phone number.
> Question: phone and walk-in enquiries look low compared with your estimate. Are some not being recorded at all?

## Limits of this approach

This works because the source happens to be the last column. If you needed a column in the *middle*, quoted commas would break it (see [Exercise 02, question 5](exercises/solutions/README.md#exercise-02--pipelines-on-leads)). For anything beyond quick exploration, use a real CSV parser, which you'll do in Python in Module 03.
