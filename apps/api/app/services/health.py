"""Service connectivity checks used by the health endpoint and worker."""

from __future__ import annotations

import time
from typing import TypedDict

import psycopg
import redis

from app.core.config import Settings


class CheckResult(TypedDict):
    ok: bool
    latency_ms: int
    detail: str


def _result(started: float, ok: bool, detail: str = "") -> CheckResult:
    return {
        "ok": ok,
        "latency_ms": int((time.monotonic() - started) * 1000),
        "detail": detail,
    }


def check_database(settings: Settings) -> CheckResult:
    started = time.monotonic()
    try:
        with (
            psycopg.connect(settings.psycopg_dsn, connect_timeout=2) as connection,
            connection.cursor() as cursor,
        ):
            cursor.execute("SELECT 1")
            cursor.fetchone()
    except Exception as exc:  # noqa: BLE001 - report failure without leaking DSNs
        return _result(started, False, type(exc).__name__)
    return _result(started, True)


def check_redis(settings: Settings) -> CheckResult:
    started = time.monotonic()
    try:
        client = redis.Redis.from_url(
            settings.redis_url,
            socket_connect_timeout=2,
            socket_timeout=2,
        )
        client.ping()
    except Exception as exc:  # noqa: BLE001 - report failure without leaking URLs
        return _result(started, False, type(exc).__name__)
    return _result(started, True)
