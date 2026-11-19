from __future__ import annotations

from fastapi.testclient import TestClient


def test_health_is_public_and_structured(client: TestClient) -> None:
    response = client.get("/api/health")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["service"] == "shortsfactory-api"
    assert body["version"] == "0.1.0"
    assert body["environment"] == "test"
    assert set(body["checks"]) == {"database", "queue"}
    assert body["checks"]["database"]["status"] == "ok"
    assert body["providers"] == {"llm": "mock", "tts": "mock", "alignment": "mock"}
    assert body["safety"] == {
        "dry_run": True,
        "upload_enabled": False,
        "publish_enabled": False,
        "approval_required": True,
        "global_emergency_stop": False,
    }


def test_health_reports_degraded_when_dependency_fails(client: TestClient, monkeypatch) -> None:
    monkeypatch.setattr(
        "app.services.health.check_redis",
        lambda _settings: {"ok": False, "latency_ms": 0, "detail": "ConnectionError"},
    )

    response = client.get("/api/health")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "degraded"
    assert body["checks"]["queue"]["status"] == "error"
    assert body["checks"]["queue"]["detail"] == "ConnectionError"


def test_root_does_not_expose_secrets(client: TestClient) -> None:
    body = client.get("/").json()
    assert body["health"] == "/api/health"
    assert "password" not in str(body).lower()
    assert "secret" not in str(body).lower()
