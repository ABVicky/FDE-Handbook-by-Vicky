"""Single sign-on with Google (OpenID Connect), added in Module 09.

The dashboard signs the counsellor in with Google (Google Identity Services) and receives an **ID token**:
a JWT signed by Google. The API verifies it and, if the person is provisioned in AdmitFlow, issues
AdmitFlow's own session token. Passwords disappear; Google enforces the institute's password and
2-step verification policies, and leavers lose access when IT disables their Google account.

Checks that matter (skipping any one of them is a security bug):
* signature, using Google's published keys (JWKS)
* `iss` is Google, `aud` is OUR client ID (otherwise a token issued to another app would work)
* not expired
* `email_verified` is true and `hd` (hosted domain) is the institute's domain
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

GOOGLE_ISSUERS = ("https://accounts.google.com", "accounts.google.com")
GOOGLE_JWKS_URL = "https://www.googleapis.com/oauth2/v3/certs"


class SsoError(Exception):
    pass


@dataclass
class SsoIdentity:
    email: str
    name: str


def verify_google_id_token(token: str, client_id: str, allowed_domain: str, jwks_client=None) -> SsoIdentity:
    import jwt

    jwks_client = jwks_client or jwt.PyJWKClient(GOOGLE_JWKS_URL)
    try:
        signing_key = jwks_client.get_signing_key_from_jwt(token)
        claims = jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256"],
            audience=client_id,
            options={"require": ["exp", "iat", "iss", "aud", "sub"]},
        )
    except jwt.PyJWTError as exc:
        raise SsoError(f"invalid ID token: {exc}") from None
    if claims.get("iss") not in GOOGLE_ISSUERS:
        raise SsoError("token not issued by Google")
    if not claims.get("email_verified"):
        raise SsoError("email not verified")
    if claims.get("hd") != allowed_domain:
        raise SsoError(f"accounts outside {allowed_domain} are not allowed")
    return SsoIdentity(email=claims["email"].lower(), name=claims.get("name", ""))


def sso_settings() -> Optional[tuple]:
    import os

    client_id, domain = os.environ.get("ADMITFLOW_GOOGLE_CLIENT_ID"), os.environ.get("ADMITFLOW_SSO_DOMAIN")
    return (client_id, domain) if client_id and domain else None
