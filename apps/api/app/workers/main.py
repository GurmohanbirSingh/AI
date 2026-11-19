"""Minimal Phase 1 worker loop: durable jobs arrive in Phase 2 (RQ selected in ADR 0002).

The worker proves queue connectivity on startup and then keeps a lightweight heartbeat.
It performs no media work and makes no external API calls.
"""

from __future__ import annotations

import logging
import signal
import time

import redis

from app.core.config import Settings, get_settings

logger = logging.getLogger("shortsfactory.worker")
HEARTBEAT_SECONDS = 30


def ping_redis(settings: Settings) -> bool:
    try:
        client = redis.Redis.from_url(
            settings.redis_url,
            socket_connect_timeout=2,
            socket_timeout=2,
        )
        return bool(client.ping())
    except Exception as exc:  # noqa: BLE001 - keep worker observable without leaking URLs
        logger.error("Redis ping failed: %s", type(exc).__name__)
        return False


def run_once(settings: Settings) -> int:
    if not ping_redis(settings):
        return 1
    logger.info(
        "Worker heartbeat OK (queue reachable, provider modes: llm=%s tts=%s)",
        settings.llm_provider,
        settings.tts_provider,
    )
    return 0


def main() -> int:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )
    settings = get_settings()
    running = True

    def _stop(signum: int, _frame: object) -> None:
        nonlocal running
        logger.info("Received signal %s, shutting down worker", signum)
        running = False

    signal.signal(signal.SIGTERM, _stop)
    signal.signal(signal.SIGINT, _stop)

    logger.info("Worker started (environment=%s)", settings.app_env)
    if not ping_redis(settings):
        logger.error("Redis is not reachable at startup; worker will retry")
    while running:
        ping_redis(settings)
        deadline = time.monotonic() + HEARTBEAT_SECONDS
        while running and time.monotonic() < deadline:
            time.sleep(0.5)
    logger.info("Worker stopped")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
