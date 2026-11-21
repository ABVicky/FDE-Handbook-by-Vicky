# Module 03 — Break & Fix: The students who never got a call

**Time:** 1–2 hours · Do this after [Lesson 08 (errors)](../lessons/08-errors-and-logging.md) and [Lesson 06 (strings)](../lessons/06-strings-and-unicode.md).

## The situation

A previous contractor wrote [`clean_ad_leads.py`](clean_ad_leads.py). Every week, reception runs it on the ad-platform export and hands the cleaned file to counsellors. It always prints `Done.` and has never shown an error.

Then Mr. Fernandes forwards a complaint:

> "A student called José Chen says he filled in our ad form and nobody ever contacted him. Another parent says the same about her daughter Zoë. Can you check?"

## Your job

1. **Reproduce it.** Run the script on the real export:
   ```bash
   python3 clean_ad_leads.py ../../../projects/admitflow/data/ad_leads.csv cleaned.csv
   ```
   Compare the number of rows in and out.
2. **Find the root cause.** There are **two** problems working together. One causes the damage, and the other hides it.
3. **Fix both**, without rewriting the whole script.
4. **Prove it:** write at least three `pytest` tests that would have caught the bug.
5. **Write the incident note** (5–8 lines, for Mr. Fernandes): what happened, how many students were affected, what you fixed, what should happen next for the affected students.

## Rules

- Change as little as possible. Explain every change.
- The fixed script must **never silently lose a row**. If it rejects something, it must say which line and why.

## Hints

<details><summary>Hint 1</summary>
Count rows: <code>wc -l</code> on input and output. Then compare the names that went in with the names that came out. What do the missing ones have in common?
</details>

<details><summary>Hint 2</summary>
Look at <code>VALID_NAME</code>. Which characters does <code>[A-Za-z]</code> actually allow? Try <code>VALID_NAME.match("José")</code> in the Python REPL.
</details>

<details><summary>Hint 3</summary>
Why did nobody notice for months? Read the <code>except</code> block. What does <code>except Exception: continue</code> do with <em>every</em> error, including ones nobody predicted?
</details>

When you're done: [SOLUTION.md](SOLUTION.md)
