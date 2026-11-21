# Break & Fix — Solution

> ⚠️ Try for real first. The struggle is the lesson.

| # | Symptom | Diagnosis | Fix | Prevention |
| --- | --- | --- | --- | --- |
| 1 | `permission denied: ./start.sh` | The file has no **execute** permission: `ls -l` shows `-rw-r--r--` | `chmod +x start.sh` (or run it with `bash start.sh`) | Commit scripts with the execute bit set; check with `ls -l` |
| 2 | Python traceback ending in `KeyError: 'ADMITFLOW_DATA_DIR'` | The server reads a **required environment variable** that nobody set | `export ADMITFLOW_DATA_DIR=/full/path/to/projects/admitflow/data`, or add it to `start.sh` | Document required variables (e.g. a `.env.example`); fail with a clear message instead of a traceback |
| 3 | Server prints `listening on http://localhost:8000`, but `curl localhost:8800` gives `Connection refused` | `start.sh` sets `PORT`, but `server.py` reads **`APP_PORT`**, so it falls back to its default, 8000 | Change `export PORT=8800` to `export APP_PORT=8800` in `start.sh` | Use one name for each setting everywhere; print the effective config at startup |

## The fixed `start.sh`

```bash
#!/usr/bin/env bash
# Starts the AdmitFlow status server.
# Expected: the app is available at http://localhost:8800

export APP_PORT=8800
export ADMITFLOW_DATA_DIR="$(cd "$(dirname "$0")/../../../../projects/admitflow/data" && pwd)"

cd "$(dirname "$0")"
python3 server.py
```

## How a pro would have found #3 quickly

```bash
lsof -nP -iTCP -sTCP:LISTEN | grep -i python   # which port is Python actually listening on?
```

```bash
grep -n "environ" server.py                     # which variables does the code read?
```

## What this teaches

These three failures (**permissions, missing configuration, wrong port**) are among the most common reasons software "doesn't work" in a customer environment. On a client site you won't get a handover note this clear, and the error may be buried in a log file. The method is the same: read the error, form a hypothesis, test it with one command, fix one thing at a time.
