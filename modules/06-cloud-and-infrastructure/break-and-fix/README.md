# Module 06 — Break & Fix: "Works on my laptop"

**Time:** 1–2 hours · Do this after [Lesson 04](../lessons/04-docker-compose.md) and [Lesson 07](../lessons/07-config-secrets-releases.md).

## The situation

Another engineer deployed AdmitFlow to the institute's office VM (`10.20.0.15`) before going on leave. You've been handed:

- [`handover/docker-compose.yml`](handover/docker-compose.yml)
- [`handover/notes-from-previous-engineer.md`](handover/notes-from-previous-engineer.md)
- logs from four attempts to get it working: [`logs-api.txt`](handover/logs-api.txt), [`logs-curl.txt`](handover/logs-curl.txt), [`logs-browser.txt`](handover/logs-browser.txt)

Mr. Fernandes: *"Counsellors can't log in. The pilot starts Monday."*

The logs are illustrative but realistic. You don't need Docker to do this exercise: diagnosing from configuration and logs, without direct access, is exactly what FDEs often have to do. (If you have Docker, reproduce it for extra credit.)

## Your job

There are **four** separate configuration problems, each of which hides the next one. For each:

| # | Symptom (quote the log line) | Root cause | Fix (exact change) | How to stop it happening again |
| --- | --- | --- | --- | --- |

Then:
1. Write the corrected `docker-compose.yml`.
2. Write a short go-live checklist that would have caught all four before Monday.
3. Write a 5-line message to Mr. Fernandes: what was wrong (no jargon), what's fixed, and when counsellors can log in.

## Hints

<details><summary>Hint 1</summary>Inside a container, <code>127.0.0.1</code> means <em>the container itself</em>. Which address must a server listen on so that traffic forwarded from outside the container can reach it?</details>

<details><summary>Hint 2</summary>The same rule applies to <code>DATABASE_URL</code>. In Compose, how does one service reach another?</details>

<details><summary>Hint 3</summary>The browser's origin is <code>http://10.20.0.15:8080</code>. Compare it, character for character, with <code>ADMITFLOW_CORS_ORIGINS</code>.</details>

<details><summary>Hint 4</summary>Read the last error. Which required variable does the Compose file never set? Where should its value come from?</details>

When you're done: [SOLUTION.md](SOLUTION.md)
