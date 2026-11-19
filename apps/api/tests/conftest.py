from __future__ import annotations

import pytest
from app.core.config import Settings
from app.main import create_app
from fastapi.testclient import TestClient


@pytest.fixture()
def settings() -> Settings:
    return Settings(
        app_env="test",
        auth_required=True,
        admin_password="test-operator-password",
        session_secret="test-session-secret-value-1234567890",
        database_url="postgresql+psycopg://user:pass@localhost:5432/test",
        redis_url="redis://localhost:6379/15",
        llm_provider="mock",
        tts_provider="mock",
        alignment_provider="mock",
    )


@pytest.fixture()
def authless_settings() -> Settings:
    return Settings(
        app_env="test",
        auth_required=False,
        admin_password="test-operator-password",
        session_secret="test-session-secret-value-1234567890",
    )


@pytest.fixture()
def client(settings: Settings, monkeypatch: pytest.MonkeyPatch) -> TestClient:
    monkeypatch.setattr(
        "app.services.health.check_database",
        lambda _settings: {"ok": True, "latency_ms": 1, "detail": ""},
    )
    monkeypatch.setattr(
        "app.services.health.check_redis",
        lambda _settings: {"ok": True, "latency_ms": 1, "detail": ""},
    )
    return TestClient(create_app(settings))


@pytest.fixture()
def authless_client(authless_settings: Settings, monkeypatch: pytest.MonkeyPatch) -> TestClient:
    monkeypatch.setattr(
        "app.services.health.check_database",
        lambda _settings: {"ok": True, "latency_ms": 1, "detail": ""},
    )
    monkeypatch.setattr(
        "app.services.health.check_redis",
        lambda _settings: {"ok": True, "latency_ms": 1, "detail": ""},
    )
    return TestClient(create_app(authless_settings))
