"""Local operator login, session introspection, and logout."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Response, status

from app.core.auth import (
    CSRF_COOKIE,
    SESSION_COOKIE,
    OperatorSession,
    SessionManager,
    get_operator_session,
    get_session_manager,
    require_csrf,
    require_operator,
)
from app.core.config import Settings, get_settings
from app.schemas.system import LoginIn, LoginOut, OperatorOut

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=LoginOut)
def login(
    body: LoginIn,
    response: Response,
    settings: Settings = Depends(get_settings),
    manager: SessionManager = Depends(get_session_manager),
) -> LoginOut:
    if not manager.verify_password(body.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid operator credentials",
        )
    token, session = manager.create()
    response.set_cookie(
        key=SESSION_COOKIE,
        value=token,
        max_age=settings.session_max_age_seconds,
        httponly=True,
        samesite="lax",
        secure=settings.cookie_secure,
        path="/",
    )
    response.set_cookie(
        key=CSRF_COOKIE,
        value=session.csrf_token,
        max_age=settings.session_max_age_seconds,
        httponly=False,
        samesite="lax",
        secure=settings.cookie_secure,
        path="/",
    )
    return LoginOut(
        authenticated=True,
        subject=session.subject,
        csrf_token=session.csrf_token,
        auth_required=settings.auth_required,
    )


@router.get("/me", response_model=OperatorOut)
def me(
    settings: Settings = Depends(get_settings),
    session: OperatorSession | None = Depends(get_operator_session),
) -> OperatorOut:
    if session is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Operator session required",
        )
    return OperatorOut(
        authenticated=True,
        subject=session.subject,
        csrf_token=session.csrf_token,
        auth_required=settings.auth_required,
    )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    response: Response,
    session: OperatorSession = Depends(require_csrf),
) -> Response:
    response.delete_cookie(SESSION_COOKIE, path="/")
    response.delete_cookie(CSRF_COOKIE, path="/")
    response.status_code = status.HTTP_204_NO_CONTENT
    return response


__all__ = ["router", "require_operator"]
