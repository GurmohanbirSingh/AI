#!/usr/bin/env python3
"""Confirm the local configuration still enforces no-upload/no-paid-API defaults."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def read_env() -> dict[str, str]:
    values: dict[str, str] = {}
    env_file = ROOT / ".env"
    if not env_file.exists():
        env_file = ROOT / ".env.example"
    for raw in env_file.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if line and not line.startswith("#") and "=" in line:
            key, value = line.split("=", 1)
            values[key.strip()] = value.strip()
    return values


def main() -> int:
    env = read_env()
    expected = {
        "DRY_RUN": "true",
        "UPLOAD_ENABLED": "false",
        "PUBLISH_ENABLED": "false",
        "APPROVAL_REQUIRED": "true",
        "GLOBAL_EMERGENCY_STOP": "false",
        "MAX_DAILY_LLM_COST": "0",
        "MAX_DAILY_TTS_COST": "0",
        "MAX_DAILY_UPLOADS": "0",
    }
    failures = [f"{key}={env.get(key)!r} (expected {value!r})" for key, value in expected.items() if env.get(key) != value]
    if env.get("LLM_PROVIDER") not in {"mock", "ollama"}:
        failures.append(
            "LLM_PROVIDER=" + repr(env.get("LLM_PROVIDER")) + " is not a local $0 provider"
        )
    if env.get("TTS_PROVIDER") not in {"mock", "kokoro", "piper"}:
        failures.append("TTS_PROVIDER=" + repr(env.get("TTS_PROVIDER")) + " is not a local $0 provider")

    if failures:
        print("FAIL: safety defaults")
        for failure in failures:
            print(f"  - {failure}")
        return 1
    print("PASS: dry run, no uploads, no publishing, no paid providers")
    print("This is a configuration check only; it does not render or upload anything.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
