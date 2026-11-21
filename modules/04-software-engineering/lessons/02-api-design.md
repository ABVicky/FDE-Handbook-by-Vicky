# Lesson 02 — Designing HTTP APIs

**Time:** ~4 hours · **Core**

## Why this matters

An API is a contract. Your frontend depends on it, and soon other systems will too: the website form, the CRM, an AI agent. A clear, predictable API is easy to use correctly and hard to misuse. A messy one generates support requests for as long as it exists.

## Resources, not actions

REST-style APIs are organized around **resources** (nouns) and use HTTP **methods** (verbs):

| Action | Method + path | Success code |
| --- | --- | --- |
| List leads | `GET /leads` | 200 |
| Get one lead | `GET /leads/{lead_id}` | 200 |
| Create a lead | `POST /leads` | 201 |
| Update part of a lead | `PATCH /leads/{lead_id}` | 200 |
| Add a note to a lead | `POST /leads/{lead_id}/notes` | 201 |
| Schedule a follow-up | `POST /leads/{lead_id}/followups` | 201 |
| Complete a follow-up | `POST /followups/{id}/complete` | 200 |

Prefer `/leads/{id}` over `/getLead?id=…`. Use plural nouns. Nest only one level (`/leads/{id}/notes`), not five.

Some operations aren't simple field updates ("complete", "send", "approve"). A small action sub-resource like `POST /followups/{id}/complete` is clearer than pretending it's a field change.

## Status codes that tell the truth

| Code | Use it when |
| --- | --- |
| `200 OK` | Success with a body |
| `201 Created` | Something new was created |
| `204 No Content` | Success, nothing to return (e.g. delete) |
| `400 Bad Request` | Malformed request |
| `401 Unauthorized` | Not logged in / bad or expired token |
| `403 Forbidden` | Logged in but not allowed |
| `404 Not Found` | The resource doesn't exist (or the caller mustn't know it exists) |
| `409 Conflict` | Clashes with current state (e.g. duplicate that can't be merged) |
| `422 Unprocessable Entity` | Validation failed (FastAPI's default) |
| `429 Too Many Requests` | Rate limited |
| `500` | Bug on the server. Never return this on purpose |

## A consistent error shape

Pick one error format and use it everywhere. AdmitFlow uses:

```json
{"error": {"status": 422, "detail": [{"field": "phone", "message": "not a valid phone number"}]}}
```

The frontend can then show any error the same way (see `web/src/api.ts`).

## Filtering, searching, pagination

```
GET /leads?status=new&source=whatsapp&search=nguyen&page=2&page_size=25
```

```json
{"items": [...], "total": 190, "page": 2, "page_size": 25}
```

- **Always cap page size** (AdmitFlow: max 100). Otherwise one request can ask for a million rows.
- Return the **total** so the UI can show "Page 2 of 8."
- *Stretch:* for very large or fast-changing data, **cursor pagination** (`?after=<last_id>`) is more reliable than page numbers.

## Validation at the edge

Validate **every** input at the API boundary: types, lengths, allowed values, formats. Reject bad data with `422` and a message saying exactly which field is wrong. Once data is inside your system, the rest of your code can trust it.

## Versioning and changes

Once others depend on your API:
- **Adding** fields or endpoints is safe.
- **Removing or renaming** fields breaks clients. Add the new one, deprecate the old one, remove it later.
- For bigger changes, version the API (`/v2/leads`) or use a version header.

## Idempotency (you'll need this in Module 09)

`GET`, `PUT` and `DELETE` should be **idempotent**: doing them twice has the same effect as once. `POST` usually isn't, so a retried `POST /leads` could create two leads. AdmitFlow's dedupe protects against that for leads. Module 09 covers idempotency keys for integrations.

## Documenting it

FastAPI generates interactive docs at `/docs` from your code. Add what generated docs can't explain: the purpose, workflows and conventions. Use the [API documentation template](../../../templates/api-documentation.md).

*Stretch:* **GraphQL** lets clients request exactly the fields they need in one query. It's useful when many different clients need different shapes of data, but it adds complexity. REST is the right default for most FDE work.

## Check yourself

Design the API (methods, paths, status codes, request and response bodies) for **campus visits**: a counsellor books a visit for a lead at a date and time, can reschedule or cancel it, and can list upcoming visits. Compare with the solution in [Exercise 01](../exercises/01-api-design.md).

Next: [Lesson 03 — FastAPI fundamentals](03-fastapi.md)
