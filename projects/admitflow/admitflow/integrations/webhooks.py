"""Verifying signed webhooks.

The website form posts each submission to AdmitFlow with three headers:

    X-AdmitFlow-Event-Id:  unique per submission (used for idempotency)
    X-AdmitFlow-Timestamp: Unix seconds when it was sent
    X-AdmitFlow-Signature: "sha256=" + HMAC-SHA256(secret, f"{timestamp}.{raw body}")

Signing the timestamp with the body stops replays of old requests; comparing in constant time
stops timing attacks. This is the same pattern Stripe, GitHub and most webhook senders use.
"""
from __future__ import annotations

import hashlib
import hmac
import time
from typing import Optional

TOLERANCE_SECONDS = 300


class WebhookError(Exception):
    pass


def sign(secret: str, timestamp: str, body: bytes) -> str:
    mac = hmac.new(secret.encode(), f"{timestamp}.".encode() + body, hashlib.sha256)
    return "sha256=" + mac.hexdigest()


def verify(secret: str, timestamp: Optional[str], body: bytes, signature: Optional[str],
           now: Optional[float] = None, tolerance: int = TOLERANCE_SECONDS) -> None:
    """Raise WebhookError unless the signature is valid and recent."""
    if not timestamp or not signature:
        raise WebhookError("missing signature headers")
    try:
        sent = int(timestamp)
    except ValueError:
        raise WebhookError("bad timestamp") from None
    if abs((now if now is not None else time.time()) - sent) > tolerance:
        raise WebhookError("timestamp outside the allowed window (possible replay)")
    if not hmac.compare_digest(sign(secret, timestamp, body), signature):
        raise WebhookError("signature mismatch")
