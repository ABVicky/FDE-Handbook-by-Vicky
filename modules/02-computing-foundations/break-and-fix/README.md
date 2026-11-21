# Module 02 — Break & Fix: "It won't start"

**Time:** 45–90 minutes · Do this after [Lesson 07](../lessons/07-troubleshooting.md).

## The situation

A colleague has left you the AdmitFlow **status server**: a tiny web app that reports how many leads are in the sample data file. Their handover note says:

> "Run `./start.sh` in the `app/` folder. The app will be at http://localhost:8800. `/health` should say ok and `/leads/count` should return 120."

It doesn't work. There are **three separate problems**. Fix all three so that both of these succeed:

```bash
curl http://localhost:8800/health
```

```bash
curl http://localhost:8800/leads/count
```

Expected output: `{"status": "ok"}` and `{"leads": 120}`.

## Rules

- Use the terminal. Read error messages slowly, word by word.
- Don't rewrite the app. Each fix is small (one command or one line).
- Write down each problem as you find it, using this format:

| # | Symptom (what you saw) | Diagnosis (why) | Fix | How to prevent it next time |
| --- | --- | --- | --- | --- |

## Files

- [`app/start.sh`](app/start.sh): the start script
- [`app/server.py`](app/server.py): the server (Python standard library only, no installs needed)
- The data file lives in [`projects/admitflow/data/`](../../../projects/admitflow/data/leads_sample.csv)

## Hints (open one at a time, only if stuck for 15+ minutes)

<details><summary>Hint 1</summary>
The first error doesn't come from Python at all. What does the shell say, and what does <code>ls -l start.sh</code> show?
</details>

<details><summary>Hint 2</summary>
Python prints a traceback. The last line tells you the exact name of something it looked for and didn't find. Which lesson covered that kind of thing?
</details>

<details><summary>Hint 3</summary>
If the server says it is "listening", believe it, and check <em>where</em>. Compare the port it prints with the port in the handover note. Then compare the variable name the script sets with the one the server reads.
</details>

When you're done: [SOLUTION.md](SOLUTION.md)
