-- Module 05 — SQL drills: reference answers.
-- Each answer starts with a "-- Q<n>" line; check_sql_drills.py runs them in order.

-- Q1: How many leads are there?
SELECT COUNT(*) FROM leads;

-- Q2: How many leads per status, most common first?
SELECT status, COUNT(*) AS n FROM leads GROUP BY status ORDER BY n DESC, status;

-- Q3: The 5 most recent leads: id, name, received_at.
SELECT lead_id, name, received_at FROM leads ORDER BY received_at DESC, lead_id LIMIT 5;

-- Q4: Leads with no phone AND no email.
SELECT lead_id, name FROM leads WHERE phone IS NULL AND email IS NULL ORDER BY lead_id;

-- Q5: Number of leads per channel (a lead counts once per channel it used).
SELECT s.source, COUNT(*) AS n
FROM lead_sources AS s
GROUP BY s.source
ORDER BY n DESC, s.source;

-- Q6: Leads that used more than one channel, with their channel count.
SELECT l.lead_id, l.name, COUNT(s.source) AS channels
FROM leads AS l
JOIN lead_sources AS s ON s.lead_id = l.lead_id
GROUP BY l.lead_id, l.name
HAVING COUNT(s.source) > 1
ORDER BY channels DESC, l.lead_id;

-- Q7: Enrolments and conversion rate per course (courses with at least one lead), best first.
SELECT course,
       COUNT(*) AS leads,
       SUM(CASE WHEN status = 'enrolled' THEN 1 ELSE 0 END) AS enrolled,
       ROUND(1.0 * SUM(CASE WHEN status = 'enrolled' THEN 1 ELSE 0 END) / COUNT(*), 3) AS conversion
FROM leads
GROUP BY course
ORDER BY conversion DESC, course;

-- Q8: Speed: average days from enquiry to enrolment, per channel (enrolled leads only).
SELECT s.source,
       ROUND(AVG(julianday(l.enrolled_on) - julianday(l.received_at)), 1) AS avg_days
FROM leads AS l
JOIN lead_sources AS s ON s.lead_id = l.lead_id
WHERE l.status = 'enrolled'
GROUP BY s.source
ORDER BY avg_days, s.source;

-- Q9 (window function): For each course, the first lead received (earliest), using ROW_NUMBER.
WITH ranked AS (
    SELECT lead_id, course, received_at,
           ROW_NUMBER() OVER (PARTITION BY course ORDER BY received_at, lead_id) AS rn
    FROM leads
)
SELECT course, lead_id, received_at FROM ranked WHERE rn = 1 ORDER BY course;

-- Q10 (CTE + window): Leads per week (weeks start on Monday) with a running total.
WITH weekly AS (
    SELECT strftime('%Y-%W', received_at) AS week, COUNT(*) AS n
    FROM leads
    GROUP BY week
)
SELECT week, n, SUM(n) OVER (ORDER BY week) AS running_total
FROM weekly
ORDER BY week;
