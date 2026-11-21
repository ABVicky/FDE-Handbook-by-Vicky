# Lesson 04 — Authentication and authorization

**Time:** ~5 hours · **Core**

## Why this matters

AdmitFlow holds students' names, phone numbers and emails. One mistake in auth, and anyone on the internet can read or change them. A data-protection complaint (Ms. Chen's worry in Module 01) can end an engagement. Auth is the part of the system where "mostly works" isn't acceptable.

| | Question | AdmitFlow example | Failure code |
| --- | --- | --- | --- |
| **Authentication** | *Who are you?* | Logging in; verifying the token on each request | `401` |
| **Authorization** | *Are you allowed to do this?* | Only admins assign leads; counsellors edit only their own | `403` |

## Storing passwords

**Never store passwords.** Store a **slow, salted hash**:

```python
import base64, hashlib, hmac, secrets

ITERATIONS = 600_000   # OWASP's recommendation for PBKDF2-HMAC-SHA256

def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, ITERATIONS)
    return f"pbkdf2_sha256${ITERATIONS}${base64.b64encode(salt).decode()}${base64.b64encode(digest).decode()}"

def verify_password(password: str, stored: str) -> bool:
    _, iterations, salt, digest = stored.split("$")
    candidate = hashlib.pbkdf2_hmac("sha256", password.encode(), base64.b64decode(salt), int(iterations))
    return hmac.compare_digest(candidate, base64.b64decode(digest))
```

- **Salt** (random per user): identical passwords get different hashes, and precomputed tables are useless.
- **Slow** (many iterations): each guess costs an attacker real time.
- **`compare_digest`**: constant-time comparison, so response timing doesn't leak information.

In production code, prefer a maintained library (e.g. `argon2-cffi` or `passlib`). AdmitFlow uses the standard library so it runs on locked-down machines.

## Sessions vs. tokens

After login, the server must recognize the user on later requests:

| | Server-side session | Signed token (JWT) |
| --- | --- | --- |
| How | Random session ID in a cookie; server stores who it belongs to | Server signs `{"sub": "priya", "role": "counsellor", "exp": …}`; client sends it back |
| Revocation | Easy: delete the session | Hard until it expires |
| Server storage | Needed (DB/Redis) | None |
| Typical use | Traditional web apps | APIs, mobile apps, multiple services |

AdmitFlow uses short-lived JWTs ([ADR-003](../../../projects/admitflow/docs/adr/003-token-auth.md)):

```python
import jwt   # PyJWT
from datetime import datetime, timedelta, timezone

def create_token(username, role):
    now = datetime.now(timezone.utc)
    return jwt.encode({"sub": username, "role": role, "iat": now, "exp": now + timedelta(hours=8)},
                      SECRET_KEY, algorithm="HS256")

claims = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])   # raises if tampered with or expired
```

JWTs are **signed, not encrypted**: anyone can read the payload. Never put secrets or personal data in them. Always specify `algorithms=[...]` when decoding.

The signing key is a secret: load it from an environment variable, make it long and random, and fail loudly if it's missing (see `admitflow/auth.py`).

## Protecting routes

```python
def current_user(credentials = Depends(HTTPBearer(auto_error=False)), repo = Depends(get_repo)) -> User:
    if credentials is None:
        raise HTTPException(401, "Not logged in", headers={"WWW-Authenticate": "Bearer"})
    try:
        claims = decode_token(credentials.credentials)
    except jwt.InvalidTokenError:
        raise HTTPException(401, "Not logged in or session expired")
    user = repo.get_user(claims["sub"])
    if user is None:
        raise HTTPException(401, "Not logged in")
    return user

def require_admin(user: User = Depends(current_user)) -> User:
    if user.role != "admin":
        raise HTTPException(403, "Admins only")
    return user
```

Note the lookup: the token says "priya", but we still load priya from the store, so a deleted user's token stops working.

## Authorization rules belong in one place

Write rules explicitly and test each one:

```python
if "assigned_to" in changes and user.role != "admin":
    raise HTTPException(403, "Only admins can assign leads")
if lead.assigned_to not in (None, user.username) and user.role != "admin":
    raise HTTPException(403, "This lead is assigned to another counsellor")
```

**Deny by default:** a new endpoint should require login unless you deliberately make it public. The break & fix service shows what happens when one route forgets.

## Login endpoint hygiene

- Same error for unknown user and wrong password (no user enumeration).
- Rate-limit login attempts (Module 10).
- HTTPS only in production. Tokens over plain HTTP can be stolen.

## Single sign-on (preview)

Most organizations prefer staff to log in with their existing Google or Microsoft account (SSO via **OpenID Connect**). Then the client's IT controls passwords, multi-factor authentication and leavers. Module 09 replaces AdmitFlow's passwords with Google sign-in.

## Check yourself

1. Write tests proving that (a) a token signed with a different key is rejected, (b) an expired token is rejected, (c) a counsellor gets `403`, not `401`, when assigning a lead.
2. Why does AdmitFlow look the user up in the store even though the token already contains their role?

Next: [Lesson 05 — Errors, logging, middleware and background work](05-errors-logging-middleware.md)
