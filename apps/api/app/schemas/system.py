"""Pydantic response models for health, auth, and dashboard endpoints."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

CheckStatus = Literal["ok", "error"]


class CheckOut(BaseModel):
    ok: bool
    status: CheckStatus
    latency_ms: int = Field(ge=0)
    detail: str = ""


class ProvidersOut(BaseModel):
    llm: str
    tts: str
    alignment: str


class SafetyOut(BaseModel):
    dry_run: bool
    upload_enabled: bool
    publish_enabled: bool
    approval_required: bool
    global_emergency_stop: bool


class HealthOut(BaseModel):
    status: Literal["ok", "degraded"]
    service: str = "shortsfactory-api"
    version: str
    environment: str
    checked_at: datetime
    checks: dict[str, CheckOut]
    providers: ProvidersOut
    safety: SafetyOut


class LoginIn(BaseModel):
    password: str = Field(min_length=1, max_length=1024)


class OperatorOut(BaseModel):
    authenticated: bool
    subject: str
    csrf_token: str
    auth_required: bool


class LoginOut(OperatorOut):
    pass


class DashboardOut(BaseModel):
    version: str
    environment: str
    operators_authenticated: bool
    checks: dict[str, CheckOut]
    providers: ProvidersOut
    safety: SafetyOut
