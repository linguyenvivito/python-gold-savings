from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.features.auth.profile.endpoint import router


def create_test_client() -> TestClient:
    app = FastAPI()
    app.include_router(router)
    return TestClient(app)


def test_auth_profile_get_accounts() -> None:
    client = create_test_client()

    response = client.get("/auth/profile/test")

    assert response.status_code == 200
    payload = response.json()
    assert isinstance(payload, list)
    assert payload[0]["account_name"] == "Test Account"
    assert payload[0]["profile_id"] == "18f22a43-64a1-45b6-ad48-257f79d4b4e5"