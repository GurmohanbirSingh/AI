"""Local operator authentication: signed HTTP-only session cookie + CSRF token.

Design (Phase 1):
- `POST /api/auth/login` verifies ADMIN_PASSWORD with a constant-time comparison.
- On success we issue a signed (itsdangerous) session cookie that is HTTP-only and
  SameSite=Lax, plus a CSRF token stored inside the signed payload and mirrored in a
  readable `sf_csrf` cookie for double-submit checks.
- Mutating authenticated routes must send `X-CSRF-Token` matching the session value.
- `AUTH_REQUIRED=false` disables enforcement (used for local automated tests only).
"""

from __future__ import annotations

import hmac
import secrets
from dataclasses import dataclass
from typing import Any

from fastapi import Depends, HTTPException, Request, status
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

from app.core.config import Settings, get_settings

SESSION_COOKIE = "sf_session"
CSRF_COOKIE = "sf_csrf"
CSRF_HEADER = "X-CSRF-Token"
SESSION_SALT = "shortsfactory-operator-session"


@dataclass(frozen=True)
class OperatorSession:
    subject: str
    csrf_token: str


class SessionManager:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._serializer = URLSafeTimedSerializer(
            secret_key=settings.session_secret,
            salt=SESSION_SALT,
        )

    def verify_password(self, candidate: str) -> bool:
        return hmac.compare_digest(candidate, self._settings.admin_password)

    def create(self) -> tuple[str, OperatorSession]:
        csrf_token = secrets.token_urlsafe(32)
        session = OperatorSession(subject="operator", csrf_token=csrf_token)
        payload = {"sub": session.subject, "csrf": session.csrf_token}
        return self._serializer.dumps(payload), session

    def read(self, token: str | None) -> OperatorSession | None:
        if not token:
            return None
        try:
            payload: Any = self._serializer.loads(
                token, max_age=self._settings.session_max_age_seconds
            )
        except (BadSignature, SignatureExpired):
            return None
        if not isinstance(payload, dict):
            return None
        subject = payload.get("sub")
        csrf = payload.get("csrf")
        if not isinstance(subject, str) or not isinstance(csrf, str):
            return None
        return OperatorSession(subject=subject, csrf_token=csrf)


def get_session_manager(settings: Settings = Depends(get_settings)) -> SessionManager:
    return SessionManager(settings)


def get_operator_session(
    request: Request,
    manager: SessionManager = Depends(get_session_manager),
) -> OperatorSession | None:
    return manager.read(request.cookies.get(SESSION_COOKIE))


def require_operator(
    session: OperatorSession | None = Depends(get_operator_session),
    settings: Settings = Depends(get_settings),
) -> OperatorSession:
    if not settings.auth_required:
        return OperatorSession(subject="operator", csrf_token="auth-disabled")
    if session is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Operator session required",
            headers={"WWW-Authenticate": "Session"},
        )
    return session


def require_csrf(
    request: Request,
    session: OperatorSession = Depends(require_operator),
    settings: Settings = Depends(get_settings),
) -> OperatorSession:
    if not settings.auth_required:
        return session
    header = request.headers.get(CSRF_HEADER, "")
    if not header or not hmac.compare_digest(header, session.csrf_token):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Missing or invalid CSRF token",
        )
    return session
