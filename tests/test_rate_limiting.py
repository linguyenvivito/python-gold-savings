import os
from uuid import uuid4

from fastapi.testclient import TestClient
import pytest

from main import create_app

if not os.getenv("DATABASE_URL", "").strip():
    pytest.skip("DATABASE_URL is required for integration tests", allow_module_level=True)


_app_routes = {route.path for route in create_app().routes}
if "/auth/login" not in _app_routes or "/auth/register" not in _app_routes:
    pytest.skip("Auth routes are unavailable in this backend variant", allow_module_level=True)

def test_login_rate_limit_returns_429(monkeypatch) -> None:
    monkeypatch.setenv("RATE_LIMITING_ENABLED", "true")
    monkeypatch.setenv("RATE_LIMIT_AUTH_LOGIN", "2/minute")
    monkeypatch.setenv("CORS_STRICT_ORIGIN_CHECK", "false")

    client = TestClient(create_app())
    username = f"ratelimit_{uuid4().hex[:10]}"
    client_id = f"test-client-{uuid4().hex[:8]}"

    register_response = client.post(
        "/auth/register",
        headers={"x-client-id": client_id},
        json={"username": username, "password": "password123"},
    )
    assert register_response.status_code == 201

    login_payload = {"username": username, "password": "password123"}
    first = client.post("/auth/login", headers={"x-client-id": client_id}, json=login_payload)
    second = client.post("/auth/login", headers={"x-client-id": client_id}, json=login_payload)
    third = client.post("/auth/login", headers={"x-client-id": client_id}, json=login_payload)

    assert first.status_code == 200
    assert second.status_code == 200
    assert third.status_code == 429
