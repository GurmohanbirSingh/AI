from __future__ import annotations

import pytest
from app.core.config import Settings, describe_validation_error, load_settings
from pydantic import ValidationError


def test_short_session_secret_is_rejected() -> None:
    with pytest.raises(ValidationError) as excinfo:
        Settings(session_secret="short")
    assert "SESSION_SECRET must be at least 16 characters" in str(excinfo.value)


def test_upload_cannot_be_enabled_while_dry_run_is_on() -> None:
    with pytest.raises(ValidationError) as excinfo:
        Settings(upload_enabled=True, dry_run=True)
    assert "UPLOAD_ENABLED=true requires DRY_RUN=false" in str(excinfo.value)


def test_publish_requires_upload() -> None:
    with pytest.raises(ValidationError) as excinfo:
        Settings(publish_enabled=True)
    assert "PUBLISH_ENABLED=true requires UPLOAD_ENABLED=true" in str(excinfo.value)


def test_production_rejects_placeholder_secrets() -> None:
    with pytest.raises(ValidationError) as excinfo:
        Settings(app_env="production", cookie_secure=True)
    assert "ADMIN_PASSWORD must be changed" in str(excinfo.value)


def test_openrouter_requires_key() -> None:
    with pytest.raises(ValidationError) as excinfo:
        Settings(llm_provider="openrouter", openrouter_api_key="")
    assert "OPENROUTER_API_KEY" in str(excinfo.value)


def test_validation_errors_do_not_echo_secret_values(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("SESSION_SECRET", "x" * 15)
    monkeypatch.setenv("ADMIN_PASSWORD", "super-secret-password-value")
    with pytest.raises(Exception) as excinfo:
        load_settings()
    message = str(excinfo.value)
    assert "SESSION_SECRET" in message
    assert "super-secret-password-value" not in message
    assert "x" * 15 not in message


def test_describe_validation_error_lists_fields_only() -> None:
    try:
        Settings(llm_provider="not-a-provider")
    except ValidationError as exc:
        text = describe_validation_error(exc)
    else:  # pragma: no cover
        raise AssertionError("expected validation error")
    assert "llm_provider" in text
    assert "not-a-provider" not in text
