# Exercise 01 — SQL drills on AdmitFlow data

Build the practice database (see the [exercises README](README.md)), open it with `sqlite3 ~/admitflow-practice.db`, and answer each question with **one query**. Write your answers in `my-work/m05/drills.sql`.

1. How many leads are there?
2. How many leads per status, most common first?
3. The 5 most recent leads: id, name, received time.
4. Leads with no phone **and** no email.
5. Number of leads per channel (a lead counts once per channel it used).
6. Leads that used more than one channel, with how many.
7. Enrolments and conversion rate per course, best first.
8. Average days from enquiry to enrolment, per channel (enrolled leads only).
9. *(window function)* For each course, the earliest lead received.
10. *(CTE + window)* Leads per week with a running total.
11. *(your own)* Write the query behind one question Mr. Fernandes would plausibly ask. State the question in a comment, and the exact definition of any rate.

Checks you can do yourself: Q1 = 190; Q5 sums to 203 (why more than 190?); Q6 has 11 rows; 22 leads are enrolled; Q10's last running total is 190.
