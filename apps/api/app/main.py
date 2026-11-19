"""FastAPI application factory."""

from __future__ import annotations

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import __version__
from app.api.router import api_router
from app.core.config import Settings, get_settings

logger = logging.getLogger("shortsfactory.api")


def configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )


def create_app(settings: Settings | None = None) -> FastAPI:
    configure_logging()
    active_settings = settings if settings is not None else get_settings()

    app = FastAPI(
        title="ShortsFactory AI API",
        version=__version__,
        openapi_url="/api/openapi.json",
        docs_url="/api/docs",
        redoc_url=None,
    )
    app.dependency_overrides[get_settings] = lambda: active_settings
    app.add_middleware(
        CORSMiddleware,
        allow_origins=active_settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Content-Type", "X-CSRF-Token"],
    )
    app.include_router(api_router, prefix="/api")

    @app.get("/", include_in_schema=False)
    def root() -> dict[str, str]:
        return {
            "service": "shortsfactory-api",
            "version": __version__,
            "health": "/api/health",
            "docs": "/api/docs",
        }

    logger.info(
        "API configured (env=%s, auth_required=%s, llm=%s, tts=%s, alignment=%s)",
        active_settings.app_env,
        active_settings.auth_required,
        active_settings.llm_provider,
        active_settings.tts_provider,
        active_settings.alignment_provider,
    )
    return app


app = create_app()
