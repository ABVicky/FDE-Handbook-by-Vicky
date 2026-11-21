# Exercise 01 — Model answer: campus-visits API

## Resources and endpoints

| Method + path | Who | Purpose | Success |
| --- | --- | --- | --- |
| `POST /leads/{lead_id}/visits` | Counsellor, admin | Book a visit | `201` |
| `GET /visits` | Counsellor (own), admin (all) | List visits | `200` |
| `GET /visits/{visit_id}` | Owner, admin, reception | One visit | `200` |
| `PATCH /visits/{visit_id}` | Owner, admin | Reschedule (`starts_at`, `campus`) or edit note | `200` |
| `POST /visits/{visit_id}/cancel` | Owner, admin | Cancel with a reason | `200` |
| `POST /visits/{visit_id}/attendance` | Reception, admin | Mark `attended` or `no_show` | `200` |
| `GET /campuses/{campus}/availability?date=2026-09-20` | Any logged-in user | Remaining capacity per hour slot | `200` |

Cancel and attendance are **actions** with their own rules, so they get their own sub-resources rather than generic `PATCH` fields.

## Bodies

Book:
```json
POST /leads/ENQ-0042/visits
{"starts_at": "2026-09-20T10:00", "campus": "North", "note": "Bringing a parent"}
```
Response `201`:
```json
{"visit_id": "v_8f2c", "lead_id": "ENQ-0042", "counsellor": "priya", "campus": "North",
 "starts_at": "2026-09-20T10:00", "status": "booked", "note": "Bringing a parent",
 "history": []}
```

Cancel:
```json
POST /visits/v_8f2c/cancel
{"reason": "Student unwell"}
```
→ `200` with `"status": "cancelled"`, and the history keeps the original booking.

List:
```
GET /visits?from=2026-09-20&to=2026-09-27&campus=North&status=booked&page=1&page_size=25
```
→ `{"items": [...], "total": 12, "page": 1, "page_size": 25}`, sorted by `starts_at`.

## Errors

| Situation | Code | Body detail |
| --- | --- | --- |
| Not logged in | `401` | `Not logged in or session expired` |
| Counsellor edits another counsellor's visit | `403` | `This visit belongs to another counsellor` |
| Lead or visit not found | `404` | |
| Invalid campus, time not on the hour, time in the past | `422` | field-level messages |
| Slot already has 8 visits | `409` | `{"message": "Slot full", "next_available": ["2026-09-20T11:00", …]}` |
| Cancelling an already cancelled/attended visit | `409` | `Visit is already cancelled` |

Returning `next_available` with the `409` saves the counsellor a round of guessing.

## Permissions summary

- Counsellors: book, reschedule, cancel **their own** visits; list their own.
- Reception: list today's visits for their campus; mark attendance.
- Admins: everything.

(This needs a third role, `reception`, which is worth raising with the client.)

## Open questions for the client

- Does "8 per slot" count only booked visits, or attended too? Do group visits (a student with 2 parents) count as one?
- Should students receive a confirmation and reminder message? (Module 09 integration.)
- What are the campus opening hours, and are there holidays?
