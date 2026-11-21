"""Dependencies injected into route functions (FastAPI's `Depends`)."""
from __future__ import annotations

from typing import Optional

import jwt
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from ..auth import decode_token
from ..models import User
from ..repository import Repository

bearer = HTTPBearer(auto_error=False)


def get_repo(request: Request) -> Repository:
    return request.app.state.repo


def current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer),
    repo: Repository = Depends(get_repo),
) -> User:
    """401 if the caller isn't logged in (no token, bad token, expired token)."""
    unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not logged in or session expired",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if credentials is None:
        raise unauthorized
    try:
        claims = decode_token(credentials.credentials)
    except jwt.InvalidTokenError:
        raise unauthorized from None
    user = repo.get_user(claims.get("sub", ""))
    if user is None:
        raise unauthorized
    return user


def require_admin(user: User = Depends(current_user)) -> User:
    """403 if logged in but not allowed."""
    if user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admins only")
    return user
