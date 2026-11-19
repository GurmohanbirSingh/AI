from __future__ import annotations

import pytest
from app.core.config import Settings
from app.workers import main as worker


@pytest.fixture()
def settings() -> Settings:
    return Settings(
        app_env="test",
        session_secret="test-session-secret-value-1234567890",
        redis_url="redis://localhost:6379/15",
    )


def test_run_once_reports_success_when_redis_answers(
    settings: Settings, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(worker, "ping_redis", lambda _settings: True)
    assert worker.run_once(settings) == 0


def test_run_once_reports_failure_when_redis_is_down(
    settings: Settings, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(worker, "ping_redis", lambda _settings: False)
    assert worker.run_once(settings) == 1
