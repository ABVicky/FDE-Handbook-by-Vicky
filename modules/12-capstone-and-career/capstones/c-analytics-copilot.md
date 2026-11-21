# Capstone C — Operations analytics copilot

## The client
**Greenleaf Community Clinics** (fictional): 6 clinics. Managers want answers ("How many no-shows did we have last month at Riverside, by weekday?"), but data sits in an appointment system export, a staff rota spreadsheet and a patient-feedback form. The one analyst has a three-week backlog.

## What they say
- **Operations director:** "I want managers to answer their own questions without waiting for Sam."
- **Sam (analyst):** "If it makes up numbers, managers will make bad decisions and I'll spend my life correcting them."
- **Privacy officer:** "Managers must never see individual patient details. Aggregates only, and nothing under 5 patients."

## Your data
Generate 12 months of synthetic appointments (≥ 50,000 rows), rota and feedback data with realistic patterns (seasonality, no-show rates by weekday, one clinic with a data-entry problem). **No real patient data.**

## Hard requirements
- A pipeline into a warehouse-style schema (PostgreSQL or DuckDB) with documented, tested models
- A copilot that turns questions into **read-only, validated SQL** over approved views only: an allow-list of tables/columns, row limits, timeouts, no patient identifiers, and small-number suppression (< 5)
- Shows the SQL and a plain-language explanation with every answer; says when it can't answer
- Evaluation: 80+ questions with expected results; execution accuracy; zero privacy violations; comparison with a simple baseline (pre-built dashboard)
- Monitoring of questions, failures and cost

## Questions to settle in discovery
Which ten questions do managers ask most? Which definitions are contested (what counts as a no-show)? Who signs off a metric definition?
