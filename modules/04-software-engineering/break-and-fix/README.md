# Module 04 — Break & Fix: The inherited follow-up service

**Time:** 2–3 hours · Do this after [Lesson 09](../lessons/09-engineering-practice.md).

## The situation

Before you arrived, another contractor started a small **follow-up reminder service** for the institute, then left. The handover consists of two files in [`followup_service/`](followup_service/app.py) and a message:

> "Mostly done. Tests are there. Should be easy to finish."

There is no README. When you run the tests, several fail.

## Your job

1. **Get it running.** Work out how to install and run it and its tests, from the code alone.
   ```bash
   cd followup_service
   ```
   ```bash
   python -m pytest -o addopts="" test_app.py
   ```
2. **Make every test pass** by fixing the application, not by editing the tests. (You may *add* tests.)
3. **Find the security problem.** One of the failures is a security hole. Explain what an attacker could do with it, and change the code so the same mistake can't happen again on a *new* route.
4. **Write the missing README:** what the service does, how to configure it (which environment variables), run it, test it, and any assumptions (time zones!).
5. **Write a 5-line handover note** for your engagement lead: what you found, what you fixed, what still worries you.

## Rules

- Change one thing at a time; rerun the tests after each change.
- For each failing test, write down: symptom → cause → fix.

## Hints

<details><summary>Hint 1</summary>Read each assertion message carefully: <code>assert 200 == 201</code> tells you exactly what's expected.</details>

<details><summary>Hint 2</summary>For pagination: with <code>page=1, size=10</code>, which index does <code>start</code> begin at? Which index <em>should</em> it?</details>

<details><summary>Hint 3</summary><code>can't compare offset-naive and offset-aware datetimes</code>: one side has a time zone and the other doesn't. Which side comes from the request, and which from the server?</details>

<details><summary>Hint 4</summary>Compare the decorators of every route. Which one is different? FastAPI can apply a dependency to <em>every</em> route at once.</details>

When you're done: [SOLUTION.md](SOLUTION.md)
