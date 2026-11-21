# Module 03 — Programming Fundamentals

> 💡 **In plain words:** This is where you learn to program, mainly in Python, with a little JavaScript at the end. It's the longest module, and that's okay. Go slowly and type every example yourself.
>
> 🛠️ **What you'll build:** A command-line tool that cleans Northbridge's messy enquiry files and finds students who enquired more than once.
>
> ⏭️ **You can skip for now:** Lessons 15–16 (async, Big-O) on a first pass if they feel heavy; come back before interviews. Experienced programmers: take the checkpoint.
>
> 🧭 **Comes after:** [Module 02: Computing Foundations](../02-computing-foundations/README.md) · **Leads to:** [Module 04: Software Engineering](../04-software-engineering/README.md)
>
> 🪜 **How to work through it:** read the lessons in order → try the exercises → do the build → do the break & fix → do the Field Track → tick the "Done when" list. New here? Read [Start Here](../../START-HERE.md) first.

**Stage:** 1 — Foundations · **Time:** ~6 weeks at 15–20 h/week · **Builds:** C2 (Build software)
**Prerequisites:** [Module 02](../02-computing-foundations/README.md): you're comfortable in the terminal, with a working Python 3.9+ and Git.

## Outcome

After this module you can write, test and debug real Python programs that handle messy real-world data, read and write basic JavaScript/TypeScript, and use Git and pull requests every day.

## Why this matters to an FDE

In Module 02, a shell pipeline answered one question. But Mr. Fernandes now has three exports in three formats: different columns, different date styles, names in many alphabets, the same student appearing in several files. Shell tools start giving wrong answers here, quietly.

Almost everything an FDE builds starts like this: **take data from systems you don't control, clean it, combine it, and make it useful**, then prove with tests that it's right. Python is the most common language for this work (and for AI work in Stage 3). JavaScript/TypeScript is what you'll meet in dashboards and many client integrations.

The goal isn't to memorize syntax. It's to become someone who can open an unfamiliar file, understand it, change it safely, and prove the change works.

## Checkpoint

Already program in Python? Take the [checkpoint](checkpoint.md). Score ≥ 80% **and** complete the [build](build.md) and [break & fix](break-and-fix/README.md) to move on.

## Lessons, week by week

| Week | # | Lesson | Core / Stretch | Time |
| --- | --- | --- | --- | --- |
| 1 | 01 | [Python setup: running code, the REPL, virtual environments](lessons/01-python-setup.md) | Core | 2 h |
| 1 | 02 | [Values, variables and types](lessons/02-values-and-variables.md) | Core | 3 h |
| 1 | 03 | [Control flow: if, for, while](lessons/03-control-flow.md) | Core | 3 h |
| 1 | 04 | [Functions](lessons/04-functions.md) | Core | 4 h |
| 2 | 05 | [Collections: lists, dicts, sets, tuples](lessons/05-collections.md) | Core | 5 h |
| 2 | 06 | [Strings, text and Unicode](lessons/06-strings-and-unicode.md) | Core | 4 h |
| 2 | 07 | [Files, CSV and JSON](lessons/07-files-csv-json.md) | Core | 4 h |
| 3 | 08 | [Errors, exceptions and logging](lessons/08-errors-and-logging.md) | Core | 3 h |
| 3 | 09 | [Modules, packages and dependencies](lessons/09-modules-and-packages.md) | Core | 3 h |
| 3 | 10 | [Classes and dataclasses](lessons/10-classes-and-dataclasses.md) | Core | 4 h |
| 3 | 11 | [Type hints](lessons/11-type-hints.md) | Core | 2 h |
| 4 | 12 | [Testing with pytest](lessons/12-testing-with-pytest.md) | Core | 5 h |
| 4 | 13 | [Debugging](lessons/13-debugging.md) | Core | 3 h |
| 4 | 17 | [Git and GitHub](lessons/17-git-and-github.md) | Core | 5 h |
| 5 | 14 | [Calling HTTP APIs](lessons/14-calling-http-apis.md) | Core | 3 h |
| 5 | 15 | [Async basics](lessons/15-async-basics.md) | Core | 2 h |
| 5 | 16 | [Data structures and Big-O](lessons/16-data-structures-and-big-o.md) | Core | 4 h |
| 6 | 18 | [JavaScript essentials](lessons/18-javascript-essentials.md) | Core | 5 h |
| 6 | 19 | [TypeScript basics](lessons/19-typescript-basics.md) | Core | 3 h |

Git (lesson 17) is scheduled in week 4 so you can submit the build through pull requests, but you can read it earlier. Start committing your exercises from week 1.

## Practice

[exercises/](exercises/README.md): five exercise sets (with runnable solutions) and three small practice projects.

## Build: the AdmitFlow command-line lead manager

See [build.md](build.md). Runs through weeks 3–6.

- **Starting point:** three exports in [`projects/admitflow/data/`](../../projects/admitflow/data/)
- **Goal:** a tested Python CLI that imports, normalizes, deduplicates, searches and exports leads
- **Reference solution:** [`projects/admitflow/`](../../projects/admitflow/README.md) (tag `m03`)

## Break & fix

[break-and-fix/](break-and-fix/README.md): a "working" cleaning script has been silently dropping almost half of the ad leads. Find out why, and why nobody noticed.

## Field Track

See [field-track.md](field-track.md). Write weekly status updates on your build, as if to the client.

## Done when

- [ ] All exercise sets complete, committed to your fork
- [ ] Your AdmitFlow CLI imports all three files: **190 unique leads, 15 duplicates merged**
- [ ] Your tests pass with **≥ 80% coverage**
- [ ] You merged your build through at least **three pull requests**
- [ ] The break & fix script loses no rows, and you've written the incident note
- [ ] You can read an unfamiliar 300-line Python file and explain what it does (try [`projects/admitflow/admitflow/cli.py`](../../projects/admitflow/admitflow/cli.py))
- [ ] Two weekly status updates written
- [ ] [`progress/self-assessment.md`](../../progress/self-assessment.md) updated

## Resources

See [resources.md](resources.md).

---
*Last verified: 2026-11-21 · Tested with: Python 3.9 and later, pytest 8, Node.js 20*
