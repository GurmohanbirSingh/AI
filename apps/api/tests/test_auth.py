from __future__ import annotations

from fastapi.testclient import TestClient


def test_protected_route_rejects_anonymous(client: TestClient) -> None:
    response = client.get("/api/dashboard")
    assert response.status_code == 401
    assert response.json()["detail"] == "Operator session required"


def test_login_rejects_wrong_password(client: TestClient) -> None:
    response = client.post("/api/auth/login", json={"password": "wrong"})
    assert response.status_code == 401
    assert "set-cookie" not in response.headers


def test_login_sets_session_and_csrf_cookies(client: TestClient) -> None:
    response = client.post("/api/auth/login", json={"password": "test-operator-password"})

    assert response.status_code == 200
    body = response.json()
    assert body["authenticated"] is True
    assert body["csrf_token"]
    cookies = response.headers.get_list("set-cookie")
    session_cookie = next(value for value in cookies if value.startswith("sf_session="))
    csrf_cookie = next(value for value in cookies if value.startswith("sf_csrf="))
    assert "HttpOnly" in session_cookie
    assert "HttpOnly" not in csrf_cookie
    assert "SameSite=lax" in session_cookie


def test_authenticated_session_can_read_me_and_dashboard(client: TestClient) -> None:
    login = client.post("/api/auth/login", json={"password": "test-operator-password"})
    me = client.get("/api/auth/me")
    dashboard = client.get("/api/dashboard")

    assert me.status_code == 200
    assert me.json()["subject"] == "operator"
    assert me.json()["csrf_token"] == login.json()["csrf_token"]
    assert dashboard.status_code == 200
    assert dashboard.json()["checks"]["database"]["ok"] is True
    assert "database_url" not in dashboard.text


def test_logout_requires_csrf_and_invalidates_session(client: TestClient) -> None:
    login = client.post("/api/auth/login", json={"password": "test-operator-password"})
    csrf = login.json()["csrf_token"]

    rejected = client.post("/api/auth/logout")
    assert rejected.status_code == 403

    accepted = client.post("/api/auth/logout", headers={"X-CSRF-Token": csrf})
    assert accepted.status_code == 204
    assert client.get("/api/auth/me").status_code == 401


def test_auth_can_be_disabled_for_local_tests(authless_client: TestClient) -> None:
    response = authless_client.get("/api/dashboard")
    assert response.status_code == 200
    assert response.json()["operators_authenticated"] is True
