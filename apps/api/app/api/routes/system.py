"""Public health endpoint and authenticated dashboard status endpoint."""

from __future__ import annotations

from datetime import UTC, datetime

from fastapi import APIRouter, Depends

from app import __version__
from app.core.auth import require_operator
from app.core.config import Settings, get_settings
from app.schemas.system import (
    CheckOut,
    DashboardOut,
    HealthOut,
    ProvidersOut,
    SafetyOut,
)
from app.services import health as health_service

router = APIRouter(tags=["system"])


def _providers(settings: Settings) -> ProvidersOut:
    return ProvidersOut(
        llm=settings.llm_provider,
        tts=settings.tts_provider,
        alignment=settings.alignment_provider,
    )


def _safety(settings: Settings) -> SafetyOut:
    return SafetyOut(
        dry_run=settings.dry_run,
        upload_enabled=settings.upload_enabled,
        publish_enabled=settings.publish_enabled,
        approval_required=settings.approval_required,
        global_emergency_stop=settings.global_emergency_stop,
    )


def _checks(settings: Settings) -> dict[str, CheckOut]:
    raw = {
        "database": health_service.check_database(settings),
        "queue": health_service.check_redis(settings),
    }
    return {
        name: CheckOut(
            ok=value["ok"],
            status="ok" if value["ok"] else "error",
            latency_ms=value["latency_ms"],
            detail=value["detail"],
        )
        for name, value in raw.items()
    }


@router.get("/health", response_model=HealthOut)
def health(settings: Settings = Depends(get_settings)) -> HealthOut:
    checks = _checks(settings)
    healthy = all(check.ok for check in checks.values())
    return HealthOut(
        status="ok" if healthy else "degraded",
        version=__version__,
        environment=settings.app_env,
        checked_at=datetime.now(UTC),
        checks=checks,
        providers=_providers(settings),
        safety=_safety(settings),
    )


@router.get("/dashboard", response_model=DashboardOut)
def dashboard(
    settings: Settings = Depends(get_settings),
    _session: object = Depends(require_operator),
) -> DashboardOut:
    return DashboardOut(
        version=__version__,
        environment=settings.app_env,
        operators_authenticated=True,
        checks=_checks(settings),
        providers=_providers(settings),
        safety=_safety(settings),
    )
