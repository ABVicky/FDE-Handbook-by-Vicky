# Module 04 — Checkpoint

Pass mark: **10 / 12**, plus the [build](build.md) and [break & fix](break-and-fix/README.md), to skip this module.

---

**1.** Design the URL and method for each: (a) list a lead's notes, (b) add a note to a lead, (c) mark follow-up 42 as done, (d) change a lead's status.

**2.** Which status code should each return? (a) a lead was created; (b) the request body is missing a required field; (c) no token was sent; (d) a counsellor tries to change another counsellor's lead; (e) the lead ID doesn't exist.

**3.** Why should a list endpoint paginate, and what should it return besides the items?

**4.** In FastAPI, what does declaring `def create(body: LeadCreate)` (where `LeadCreate` is a Pydantic model) give you for free?

**5.** What is `Depends()` for? Give two examples from AdmitFlow.

**6.** Why must passwords be hashed with a *slow* algorithm (PBKDF2, bcrypt, scrypt, Argon2) rather than SHA-256 alone?

**7.** What's the difference between authentication and authorization? Give an AdmitFlow example of each.

**8.** A login endpoint returns "Unknown user" for bad usernames and "Wrong password" for bad passwords. What's the problem?

**9.** Your React app at `http://localhost:5173` calls `http://localhost:8000/leads` and the browser console says *blocked by CORS policy*. What's happening and how do you fix it?

**10.** What's wrong with this React code?
```tsx
function Note({ text }: { text: string }) {
  return <div dangerouslySetInnerHTML={{ __html: text }} />;
}
```

**11.** In a `useEffect` that fetches data when a search box changes, why might results "flicker" back to older results, and how do you prevent it?

**12.** Describe the testing pyramid. Where does `TestClient(app).get("/leads")` sit?

---

<details>
<summary><strong>Answers</strong></summary>

1. (a) `GET /leads/{id}/notes` (or include them in `GET /leads/{id}`) · (b) `POST /leads/{id}/notes` · (c) `POST /followups/42/complete` or `PATCH /followups/42` with `{"done": true}` · (d) `PATCH /leads/{id}` with `{"status": "contacted"}`.
2. (a) `201` · (b) `422` (FastAPI) or `400` · (c) `401` · (d) `403` · (e) `404`.
3. Returning everything gets slower and heavier as data grows, and can time out or exhaust memory. Return the total count and page info (`total`, `page`, `page_size`, or a `next` cursor) so the client can build navigation.
4. Parsing the JSON body, validation with clear `422` errors, type conversion, editor autocompletion, and OpenAPI documentation at `/docs`.
5. Dependency injection: reusable inputs computed per request. AdmitFlow uses `get_repo` (which data store), `current_user` (decode the token, load the user, or 401) and `require_admin` (403 unless admin).
6. Fast hashes let attackers who steal the database try billions of guesses per second. Slow, salted algorithms make each guess expensive, and the salt stops precomputed tables and reveals nothing when two users share a password.
7. Authentication: *who are you?* (logging in, verifying the token). Authorization: *are you allowed?* (only admins can assign leads; counsellors can't edit others' leads).
8. It tells attackers which usernames exist (user enumeration). Return the same message for both.
9. The browser blocks cross-origin requests unless the server allows the origin. Configure the API's CORS middleware to allow `http://localhost:5173` (and the real dashboard origin in production), or serve both from the same origin via a proxy.
10. It injects raw HTML from data, so a note containing `<img src=x onerror=…>` runs script in counsellors' browsers (XSS). Render `{text}` normally; React escapes it.
11. Responses can arrive out of order: an older, slower request finishes after a newer one. Ignore stale responses (a `cancelled` flag in the effect's cleanup, or `AbortController`) and debounce typing.
12. Many fast unit tests at the bottom, fewer integration tests in the middle, a few slow end-to-end tests at the top. `TestClient` tests are **integration** tests: routing, validation, auth and storage together, but no real browser or network.

</details>
