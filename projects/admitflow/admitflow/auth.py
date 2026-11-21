"""Password hashing and access tokens (added in Module 04).

* Passwords are never stored. We store a slow, salted hash (PBKDF2-HMAC-SHA256).
* After login the API issues a short-lived signed token (JWT). The browser sends
  it on each request in the `Authorization: Bearer <token>` header.
"""
from __future__ import annotations

import base64
import hashlib
import hmac
import os
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any, Dict

import jwt  # PyJWT

ITERATIONS = 600_000          # OWASP's current recommendation for PBKDF2-HMAC-SHA256
TOKEN_TTL = timedelta(hours=8)  # one working day
ALGORITHM = "HS256"


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, ITERATIONS)
    return "pbkdf2_sha256${}${}${}".format(
        ITERATIONS, base64.b64encode(salt).decode(), base64.b64encode(digest).decode()
    )


def verify_password(password: str, stored: str) -> bool:
    try:
        scheme, iterations, salt_b64, digest_b64 = stored.split("$")
    except ValueError:
        return False
    if scheme != "pbkdf2_sha256":
        return False
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), base64.b64decode(salt_b64), int(iterations))
    # compare_digest takes the same time whether or not the strings match (no timing leaks)
    return hmac.compare_digest(digest, base64.b64decode(digest_b64))


def secret_key() -> str:
    key = os.environ.get("ADMITFLOW_SECRET_KEY")
    if not key or len(key) < 32:
        raise RuntimeError(
            "ADMITFLOW_SECRET_KEY must be set to a random value of at least 32 characters. "
            "Generate one with: python -c 'import secrets; print(secrets.token_urlsafe(48))'"
        )
    return key


def create_token(username: str, role: str, now: datetime | None = None) -> str:
    now = now or datetime.now(timezone.utc)
    payload = {"sub": username, "role": role, "iat": now, "exp": now + TOKEN_TTL}
    return jwt.encode(payload, secret_key(), algorithm=ALGORITHM)


def decode_token(token: str) -> Dict[str, Any]:
    """Raises jwt.InvalidTokenError (including ExpiredSignatureError) if the token is bad."""
    return jwt.decode(token, secret_key(), algorithms=[ALGORITHM])
