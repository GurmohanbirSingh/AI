"""Docker health check for the worker process."""

from __future__ import annotations

import logging

from app.core.config import get_settings
from app.workers.main import run_once


def main() -> int:
    logging.basicConfig(level=logging.WARNING)
    return run_once(get_settings())


if __name__ == "__main__":
    raise SystemExit(main())
