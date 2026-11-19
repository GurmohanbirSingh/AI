#!/usr/bin/env python3
"""Fail if .env.example contains something that looks like a real secret."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ENV_EXAMPLE = ROOT / ".env.example"

# Values that are clearly placeholders or empty.
SAFE_VALUES = {
    "",
    "change-me-locally",
    "change-me-to-a-random-32-byte-secret",
    "shortsfactory",
    "default",
    "mock",
    "development",
    "http://localhost:3000",
    "http://localhost:8000",
    "http://host.docker.internal:11434",
    "qwen2.5:7b",
    "tiny.en",
    "cpu",
    "int8",
    "postgresql+psycopg://shortsfactory:shortsfactory@postgres:5432/shortsfactory",
    "redis://redis:6379/0",
    "/app/data/media",
    "/app/data/temp",
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/yt-analytics.readonly",
}

# Keys that must never carry a non-placeholder value in the example file.
SECRET_KEYS = {
    "ADMIN_PASSWORD",
    "SESSION_SECRET",
    "OPENROUTER_API_KEY",
    "TTS_API_KEY",
    "PEXELS_API_KEY",
    "PIXABAY_API_KEY",
    "YOUTUBE_API_KEY",
    "YOUTUBE_CLIENT_ID",
    "YOUTUBE_CLIENT_SECRET",
    "TOKEN_ENCRYPTION_KEY",
}

OBVIOUS_SECRET = re.compile(r"^(sk-|AIza|ghp_|xox[baprs]-|ya29\.)")


def main() -> int:
    if not ENV_EXAMPLE.exists():
        print("ERROR: .env.example is missing")
        return 1

    problems: list[str] = []
    seen: set[str] = set()
    for line_number, raw in enumerate(ENV_EXAMPLE.read_text(encoding="utf-8").splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            problems.append(f"line {line_number}: not a KEY=VALUE entry")
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()
        if key in seen:
            problems.append(f"line {line_number}: duplicate key {key}")
        seen.add(key)
        if key in SECRET_KEYS and value not in SAFE_VALUES:
            problems.append(f"line {line_number}: {key} does not look like a placeholder")
        if OBVIOUS_SECRET.match(value):
            problems.append(f"line {line_number}: {key} looks like a real credential")

    required = {
        "APP_ENV",
        "AUTH_REQUIRED",
        "ADMIN_PASSWORD",
        "SESSION_SECRET",
        "DATABASE_URL",
        "REDIS_URL",
        "LLM_PROVIDER",
        "TTS_PROVIDER",
        "ALIGNMENT_PROVIDER",
        "DRY_RUN",
        "UPLOAD_ENABLED",
        "PUBLISH_ENABLED",
        "APPROVAL_REQUIRED",
    }
    missing = sorted(required - seen)
    if missing:
        problems.append("missing required keys: " + ", ".join(missing))

    expected_safety = {
        "DRY_RUN": "true",
        "UPLOAD_ENABLED": "false",
        "PUBLISH_ENABLED": "false",
        "APPROVAL_REQUIRED": "true",
        "GLOBAL_EMERGENCY_STOP": "false",
        "MAX_DAILY_LLM_COST": "0",
        "MAX_DAILY_TTS_COST": "0",
        "MAX_DAILY_UPLOADS": "0",
    }
    values: dict[str, str] = {}
    for raw in ENV_EXAMPLE.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if line and not line.startswith("#") and "=" in line:
            key, value = line.split("=", 1)
            values[key.strip()] = value.strip()
    for key, expected in expected_safety.items():
        if values.get(key) != expected:
            problems.append(f"{key} must default to {expected!r}")

    if problems:
        print("FAIL: .env.example check")
        for problem in problems:
            print(f"  - {problem}")
        return 1
    print("PASS: .env.example contains placeholders and safe defaults only")
    return 0


if __name__ == "__main__":
    sys.exit(main())
