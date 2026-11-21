# ADR-003: Short-lived signed tokens for authentication

**Status:** Accepted for the pilot · **Date:** Module 04 · **Superseded in part by:** Module 09 (SSO)

## Context
Six counsellors and one admin need to log in to the dashboard. The institute uses Google Workspace, but SSO setup needs the part-time IT admin's time, which isn't available until after the pilot.

## Decision
- Usernames and passwords stored as PBKDF2-HMAC-SHA256 hashes (600,000 iterations, random salt).
- On login, issue a JWT signed with `ADMITFLOW_SECRET_KEY`, valid for 8 hours. The browser keeps it in `sessionStorage` and sends it as `Authorization: Bearer …`.
- Roles: `counsellor` and `admin`. Only admins can assign leads; counsellors can only change leads that are unassigned or assigned to them.

## Consequences
- ✅ No server-side session store needed; works with several API instances.
- ⚠️ Tokens can't be revoked before they expire. Mitigated by the 8-hour lifetime; if a laptop is lost, rotate the secret key (logs everyone out).
- ⚠️ `sessionStorage` is readable by JavaScript, so XSS would expose the token. React's escaping and a strict Content-Security-Policy (Module 10) mitigate this.
- ➡️ Module 09 replaces passwords with Google sign-in (OpenID Connect).
