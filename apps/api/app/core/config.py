"""Typed application settings with fail-fast, non-secret-leaking validation.

Environment variable names follow Part I (Section 24) of the blueprint. Secrets are
never included in error messages: only field names and human-readable reasons are
reported so startup failures are safe to paste into logs.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import ValidationError, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

ProviderMode = Literal["mock", "ollama", "openrouter"]
TTSMode = Literal["mock", "kokoro", "piper", "api"]
AlignmentMode = Literal["mock", "whisperx", "faster-whisper"]

INSECURE_PLACEHOLDERS = {
    "change-me-locally",
    "change-me-to-a-random-32-byte-secret",
}


class ConfigError(RuntimeError):
    """Raised when required configuration is missing or unsafe."""


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_env: Literal["development", "test", "production"] = "development"
    app_base_url: str = "http://localhost:3000"
    api_base_url: str = "http://localhost:8000"
    cors_origins: str = "http://localhost:3000"

    # Local operator auth
    auth_required: bool = True
    admin_password: str = "change-me-locally"
    session_secret: str = "change-me-to-a-random-32-byte-secret"
    session_max_age_seconds: int = 60 * 60 * 12
    cookie_secure: bool = False

    # Core infrastructure
    database_url: str = (
        "postgresql+psycopg://shortsfactory:shortsfactory@postgres:5432/shortsfactory"
    )
    redis_url: str = "redis://redis:6379/0"

    # Local storage
    media_root: str = "/app/data/media"
    temp_root: str = "/app/data/temp"

    # Providers
    llm_provider: ProviderMode = "mock"
    ollama_base_url: str = "http://host.docker.internal:11434"
    ollama_model: str = "qwen2.5:7b"
    openrouter_api_key: str = ""
    openrouter_model: str = ""
    tts_provider: TTSMode = "mock"
    alignment_provider: AlignmentMode = "mock"

    # Safety switches (safe defaults must never be changed in .env.example)
    dry_run: bool = True
    upload_enabled: bool = False
    publish_enabled: bool = False
    approval_required: bool = True
    global_emergency_stop: bool = False

    # Daily caps
    max_daily_llm_cost: float = 0.0
    max_daily_tts_cost: float = 0.0
    max_daily_uploads: int = 0

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def psycopg_dsn(self) -> str:
        """psycopg accepts libpq URLs; strip the SQLAlchemy driver suffix."""
        return self.database_url.replace("postgresql+psycopg://", "postgresql://", 1)

    @model_validator(mode="after")
    def _validate_security_and_safety(self) -> Settings:
        if len(self.session_secret) < 16:
            raise ValueError("SESSION_SECRET must be at least 16 characters")
        if not self.admin_password:
            raise ValueError("ADMIN_PASSWORD must not be empty")
        if self.session_max_age_seconds <= 0:
            raise ValueError("SESSION_MAX_AGE_SECONDS must be a positive integer")

        if self.app_env == "production":
            if self.admin_password in INSECURE_PLACEHOLDERS:
                raise ValueError("ADMIN_PASSWORD must be changed from its placeholder value")
            if self.session_secret in INSECURE_PLACEHOLDERS:
                raise ValueError("SESSION_SECRET must be changed from its placeholder value")
            if not self.cookie_secure:
                raise ValueError("COOKIE_SECURE must be true when APP_ENV=production")
            if not self.auth_required:
                raise ValueError("AUTH_REQUIRED must be true when APP_ENV=production")

        if self.publish_enabled and not self.upload_enabled:
            raise ValueError("PUBLISH_ENABLED=true requires UPLOAD_ENABLED=true")
        if self.upload_enabled and self.dry_run:
            raise ValueError("UPLOAD_ENABLED=true requires DRY_RUN=false")
        if self.upload_enabled and not self.approval_required:
            raise ValueError("UPLOAD_ENABLED=true requires APPROVAL_REQUIRED=true")

        if self.llm_provider == "openrouter" and not self.openrouter_api_key:
            raise ValueError("LLM_PROVIDER=openrouter requires OPENROUTER_API_KEY")
        if self.tts_provider == "api" and not self.approval_required:
            raise ValueError("TTS_PROVIDER=api requires APPROVAL_REQUIRED=true")

        return self


def describe_validation_error(exc: ValidationError) -> str:
    """Return a secret-free description of a settings validation failure."""
    lines: list[str] = []
    for error in exc.errors():
        location = ".".join(str(part) for part in error.get("loc", ())) or "settings"
        message = str(error.get("msg", "invalid value"))
        lines.append(f"  - {location}: {message}")
    return "\n".join(lines)


def load_settings() -> Settings:
    """Validate settings at process startup with actionable, secret-free errors."""
    try:
        return Settings()
    except ValidationError as exc:
        detail = describe_validation_error(exc)
        raise ConfigError(
            "Invalid ShortsFactory configuration. Check your .env file "
            "(copy .env.example if you have not created one):\n" + detail
        ) from None


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return load_settings()
