# API Documentation — <Service name>

**Base URL:** `https://…` · **Version:** · **Auth:** <how to get and send credentials>

> If the API is built with FastAPI, the interactive reference is generated automatically at `/docs` (Swagger UI) and `/openapi.json`. This document adds what generated docs can't: purpose, workflows, error handling and examples.

## Authentication
<Step by step: how to obtain a token, how long it lasts, how to send it.>

## Conventions
- Dates/times: <format and time zone>
- Pagination: <parameters and response shape>
- Errors: <error body shape, e.g. `{"error": {"status": 422, "detail": …}}`>
- Rate limits:

## Endpoints
### `METHOD /path`
**Purpose:** · **Auth:** · **Permissions:**

Request:
```json
{}
```
Response `200`:
```json
{}
```
Errors: `401` …, `403` …, `404` …, `422` …

## Common workflows
<e.g. "Log in → list my leads → add a note → schedule a follow-up", with example requests.>

## Changelog
| Version | Date | Change |
| --- | --- | --- |
