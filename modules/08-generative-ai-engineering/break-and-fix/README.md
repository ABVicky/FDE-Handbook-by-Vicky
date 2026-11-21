# Module 08 — Break & Fix: The assistant that quotes last year's fees

**Time:** 1–2 hours · Do this after [Lesson 03](../lessons/03-rag.md).

## The situation

Before AdmitFlow had a course assistant, someone built a quick demo, [`naive_assistant.py`](naive_assistant.py). It impressed everyone. Then a parent complains:

> "Your website chat told my daughter Data Analytics costs 1,650 a term. The invoice says 1,800. Which is it?"

```bash
cd modules/08-generative-ai-engineering/break-and-fix
```

```bash
python3 naive_assistant.py "What are the fees for Data Analytics?"
```

## Your job

1. **Reproduce it.** Ask several fee questions. Which answers are wrong, and which document do they come from?
2. **Find every cause.** There's more than one. Look at how documents are split, what information is thrown away, and how many results are used.
3. **Fix it properly.** Not by deleting `fees-2025.md`: the institute keeps old fee schedules on purpose (finance and auditors need them).
4. **Prevent it.** Write a check that fails if any fee answer is outdated or missing, and add fee questions to the evaluation set.
5. **Write the reply** to the parent (≤ 80 words) and a 4-line incident note for Mr. Fernandes.

## Hints

<details><summary>Hint 1</summary>Look at the front matter at the top of <code>fees-2025.md</code>. Does the naive assistant ever read it?</details>

<details><summary>Hint 2</summary>Print the chunks. Where does the 2026 fee table end up when documents are cut every 400 characters?</details>

<details><summary>Hint 3</summary>An assistant that shows the user a raw chunk can't say "I'm not sure". What does a good answer need besides text: a source? A date?</details>

When you're done: [SOLUTION.md](SOLUTION.md)
