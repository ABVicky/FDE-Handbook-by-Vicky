# Troubleshooting library

Real errors met while building this handbook, and what they meant.

| Symptom | Cause | Fix | Where |
| --- | --- | --- | --- |
| `permission denied: ./start.sh` | No execute bit | `chmod +x` | M02 break & fix |
| `KeyError: 'ADMITFLOW_DATA_DIR'` | Required env var not set | Set it; fail with a clear message | M02 |
| Server "listening" but `Connection refused` | Wrong port (variable name mismatch) | Use one config name everywhere | M02 |
| `KeyError: 'Date'` reading a CSV that has `Date` | Excel BOM: header is `﻿Date` | `encoding="utf-8-sig"` | M03 |
| Fewer rows out than in, no error | `except Exception: continue` hiding failures | Catch specific errors; report rejects | M03 break & fix |
| "Editable mode currently requires a setuptools-based build" | Old pip (macOS system Python) | `python -m pip install --upgrade pip` in the venv | M03 L01 |
| Browser: `blocked by CORS policy` | Origin not allowed, **or a different program on the port** | Configure CORS; check `lsof -i :8000` | M04 L07 |
| `can't compare offset-naive and offset-aware datetimes` | Mixed time-zone handling | Normalize at input; test in two zones | M04 break & fix |
| Testing Library: "Found multiple elements" | No automatic cleanup without Vitest globals | `afterEach(cleanup)` | M04 Exercise 03 |
| Report takes 26 s | Correlated subquery with no index; function on a column | Composite index; compare raw column | M05 break & fix |
| SQLite migration: "Constraint must have a name" | Unnamed unique constraint in batch mode | Name it (a named unique index) | M09 |
| `Recv failure: Connection reset by peer` from a container | App bound to `127.0.0.1` inside the container | Bind `0.0.0.0` | M06 break & fix |
| `connection to server at "127.0.0.1", port 5432 failed` in Compose | `localhost` means the container itself | Use the service name (`db`) | M06 break & fix |
| Model "99% accurate" | Leakage + accuracy on imbalanced data | Remove post-outcome features; temporal split; baselines | M07 break & fix |
| Walk-ins all "out of hours" | Date-only fields parsed as midnight | Treat date-only as unknown time | M07 |
| Assistant quotes last year's fee | Metadata ignored; fixed-size chunks | Section chunks + `superseded` filter + eval | M08 break & fix |
| `ModuleNotFoundError: mcp.server.fastmcp` | MCP SDK 2.x renamed `FastMCP` to `MCPServer` | Follow the SDK's migration notes; pin versions | M09 |
| MCP tool error message hidden from client | MCP 2.x hides unexpected exceptions | Raise `ToolError` for expected errors | M09 |
| CRM has 240 contacts for 99 students | Retried creates; no stored IDs | Search-before-create; store `crm_id`; no blind retry | M09 break & fix |
| Redaction masks timestamps | Phone regex too loose | Digit-count and date checks; test on real log lines | M10 |
| Messages silently unsent for days | No alert on what users experience | Oldest-approved-message gauge + alert | M10 break & fix |
| `list_audit` returns only 100 rows | Default page size | Pass `limit` | M10 Exercise 02 |

Add yours: symptom, cause, fix, and where you met it.
