from fastapi.testclient import TestClient

from main import create_app

def test_account_health_check() -> None:
    client = TestClient(create_app())

    response = client.get("/accounts/health")

    assert response.status_code == 200

def test_account_get_accounts() -> None:
    client = TestClient(create_app())

    response = client.get("/accounts/get")

    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) > 0