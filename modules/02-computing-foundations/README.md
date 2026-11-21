# Module 02 — Computing Foundations

> 💡 **In plain words:** Here you'll get comfortable with the computer itself: the terminal (the text window developers type commands into), files, and how the internet carries a request from a browser to a server. These are the basics every later module quietly depends on.
>
> 🛠️ **What you'll build:** A small script that counts Northbridge's enquiries by channel, using only the terminal.
>
> ⏭️ **You can skip for now:** The stretch topics inside lessons. If you already use the terminal daily, take the checkpoint quiz.
>
> 🧭 **Comes after:** [Module 01: Introduction to Forward Deployed Engineering](../01-introduction-to-fde/README.md) · **Leads to:** [Module 03: Programming Fundamentals](../03-programming-fundamentals/README.md)
>
> 🪜 **How to work through it:** read the lessons in order → try the exercises → do the build → do the break & fix → do the Field Track → tick the "Done when" list. New here? Read [Start Here](../../START-HERE.md) first.

**Stage:** 1 — Foundations · **Time:** ~2 weeks at 15–20 h/week · **Builds:** C2 (Build software), C4 (Deploy and integrate)
**Prerequisites:** [Module 01](../01-introduction-to-fde/README.md). No programming experience needed.

## Outcome

After this module you can explain how computers, operating systems and the internet work well enough to install, run and troubleshoot software entirely from the terminal.

## Why this matters to an FDE

On your first day at a client, you're given a laptop with restricted permissions, a VPN, and SSH access to a server you've never seen. A service "isn't working." There's no IDE with a friendly button, just a terminal and an error message.

FDEs live in environments they didn't set up. You'll constantly need to answer questions like: *Is the process running? Which port is it on? Can this machine reach that one? Is the configuration loaded? Is it DNS?* Engineers who can answer these calmly, with a few terminal commands, earn a client's trust fast. Engineers who can't are stuck waiting for someone else.

Everything in later modules (Python, databases, Docker, cloud, AI services) runs on top of the ideas here: processes, files, permissions, environment variables, ports and HTTP.

## Checkpoint

Already comfortable with the terminal and networking? Take the [checkpoint](checkpoint.md). Score ≥ 80% **and** complete the [build task](build.md) and [break & fix](break-and-fix/README.md) to skip ahead.

## Before you start

Set up your machine with the [setup guide](setup.md) (about 1 hour). **Windows users:** install WSL (Windows Subsystem for Linux). Every command in this handbook assumes a Linux/macOS-style shell.

## Lessons

| # | Lesson | Core / Stretch | Time |
| --- | --- | --- | --- |
| 01 | [How computers run programs](lessons/01-how-computers-work.md) | Core | 2 h |
| 02 | [Operating systems, files and permissions](lessons/02-operating-systems-and-files.md) | Core | 3 h |
| 03 | [The command line](lessons/03-command-line.md) | Core | 5 h |
| 04 | [Environment variables, PATH and installing software](lessons/04-environment-and-path.md) | Core | 2 h |
| 05 | [Networking fundamentals](lessons/05-networking.md) | Core | 3 h |
| 06 | [HTTP and the client–server model](lessons/06-http-and-client-server.md) | Core | 3 h |
| 07 | [Troubleshooting like an engineer](lessons/07-troubleshooting.md) | Core | 2 h |

Stretch topics (shell scripting in depth, compilers vs. interpreters, WSL internals) are flagged inside the lessons.

## Practice

[exercises/](exercises/README.md): four hands-on exercises using the AdmitFlow sample data. Solutions are in [exercises/solutions/](exercises/solutions/README.md).

## Build: count leads from the terminal

See [build.md](build.md).

- **Starting point:** [`projects/admitflow/data/leads_sample.csv`](../../projects/admitflow/data/leads_sample.csv), 120 synthetic enquiries
- **Goal:** a shell script that prints how many leads came from each channel, handling messy data
- **Reference solution:** [build-solution.md](build-solution.md)

## Break & fix

[break-and-fix/](break-and-fix/README.md): a small web app won't start. Find the three problems: permissions, a missing environment variable, and a port mismatch.

## Field Track

See [field-track.md](field-track.md). Explain "what happens when you type a web address" to a non-technical person in under 200 words, then test your explanation on a real person.

## Done when

- [ ] Your dev environment passes the [setup checklist](setup.md#final-check)
- [ ] You can install, run and stop a program entirely from the terminal
- [ ] You can explain DNS, ports and HTTP status codes without notes
- [ ] Your `count_by_source.sh` script gives the correct counts on the sample data
- [ ] The break & fix app returns `{"leads": 120}` on port 8800, and you've written up all three fixes
- [ ] Your Field Track explanation was tested on a real person, and you revised it based on their feedback
- [ ] [`progress/self-assessment.md`](../../progress/self-assessment.md) updated

## Resources

See [resources.md](resources.md).

---
*Last verified: 2026-11-21 · Tested with: bash 3.2+/zsh 5 on macOS, bash 5 on Ubuntu 24.04, Python 3.9+*
