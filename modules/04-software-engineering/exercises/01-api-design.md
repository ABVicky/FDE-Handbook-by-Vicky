# Exercise 01 — Design the campus-visits API

Counsellors want to book **campus visits** for prospective students.

Requirements from the Head of Admissions:
- A counsellor books a visit for a lead: date, time, campus (North or South), optional note.
- Visits can be rescheduled or cancelled (cancelled visits stay in history, with a reason).
- Counsellors see their upcoming visits; admins see everyone's.
- Each campus can host at most **8 visits per hour slot**.
- Reception marks a visit as **attended** or **no-show** on the day.

Design the API on paper (a Markdown file is fine):
1. Resources, methods, paths
2. Request and response bodies (JSON examples)
3. Status codes for success **and** for each failure (including the 8-per-slot rule)
4. Who is allowed to do what
5. Query parameters for listing (filters, pagination)
6. One open question you'd ask the client before building it
