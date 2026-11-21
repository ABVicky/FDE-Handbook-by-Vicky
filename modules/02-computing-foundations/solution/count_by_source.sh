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

# 1. drop the header      2. strip Windows \r     3. skip blank lines
# 4. take the LAST field (source), so commas inside quoted names don't matter
# 5. normalise: lower-case and remove surrounding spaces
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
