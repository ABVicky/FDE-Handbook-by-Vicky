# Module 10 — Break & Fix: The follow-ups nobody sent

**Time:** 2 hours · Do this after [Lesson 05](../lessons/05-monitoring-and-alerting.md) and [Lesson 07](../lessons/07-incidents.md).

## The situation

Thursday 10:15. A parent calls Mr. Fernandes: *"My son enquired on Monday. Your counsellor told him to expect a WhatsApp message. Nothing came."*

Counsellors say they approved dozens of follow-ups this week. AdmitFlow's dashboard shows them as approved. Nothing looks broken.

Replay the week:

```bash
cd modules/10-production-security-reliability/break-and-fix
```

```bash
python simulate_incident.py
```

```
follow-ups approved over 3 days: 54
sent: 24   still waiting: 30   (oldest approved Mon 14:00)
warnings written to the log: 1125   alerts raised: 0
```

Open the log file it prints.

## Your job

1. **Diagnose:** what failed, when, and why did nobody notice for three days? Name at least **three** separate reasons it went undetected.
2. **Mitigate:** what exactly would you do in the first 30 minutes on Thursday (in order)?
3. **Detect next time:** which metric and alert would have caught it, and how soon? Prove it by running the simulation with your alert.
4. **Prevent:** what else should change (credentials, scheduling, process)?
5. **Write the incident report** with the [template](../../../templates/incident-report.md), and the message to Mr. Fernandes and to affected students.

## Hints

<details><summary>Hint 1</summary>Read one line of the log. Is the error something retrying will ever fix?</details>

<details><summary>Hint 2</summary>What does the scheduler do with <code>send-approved</code>'s exit code? Who reads that log file?</details>

<details><summary>Hint 3</summary>What does a student experience? Measure <em>that</em> (how long approved messages wait), not just whether the process ran.</details>

When you're done: [SOLUTION.md](SOLUTION.md)
