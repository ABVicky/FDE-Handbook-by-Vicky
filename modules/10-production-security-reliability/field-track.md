# Module 10 — Field Track: Game day

**Time:** ~2.5 hours with a partner · **Capabilities:** C4, C5

## Why

You don't want the first real incident to be your first practice. A **game day** deliberately breaks a staging system so the team practises detecting, responding and communicating, and finds missing alerts and wrong runbook steps while it's safe.

## Setup

Run AdmitFlow locally or in staging with Compose, metrics and (ideally) Prometheus with `alerts.yml`. Your partner plays the saboteur *and* Mr. Fernandes.

## The game

Your partner secretly introduces **three** faults, one at a time, e.g.:
- stop the database container
- set a wrong `WHATSAPP_TOKEN` and approve some drafts
- fill the assistant's documents folder with an empty or broken file
- remove the webhook secret
- revoke a counsellor's account while they're logged in

For each one, you:
1. **Detect** it (from alerts and metrics, not from your partner telling you)
2. **Communicate:** send "Mr. Fernandes" an update within 10 minutes of detecting it
3. **Mitigate** using the runbook (and note any step that's missing or wrong)
4. **Confirm recovery** with a metric or check

## Afterwards (45 minutes)

- Write a short incident report for the most serious fault ([template](../../templates/incident-report.md))
- Update the runbook with everything that was missing
- List any alert that should have fired and didn't, and add it

## Done when

- [ ] Three faults detected, communicated and recovered
- [ ] Time to detect and time to recover recorded for each
- [ ] Runbook and alerts improved from what you learned
- [ ] One incident report written
