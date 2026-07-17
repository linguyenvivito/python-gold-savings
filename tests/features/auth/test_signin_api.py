from fastapi.testclient import TestClient

from main import create_app
from src.core.supabase_connection import get_db


class FakeSession:
    access_token = "access-token"
    refresh_token = "refresh-token"
    token_type = "bearer"


class FakeUser:
    id = "18f22a43-64a1-45b6-ad48-257f79d4b4e1"
    email = "jane@example.com"


class FakeSignInResponse:
    def __init__(self, session: FakeSession | None, user: FakeUser | None) -> None:
        self.session = session
        self.user = user


class FakeAuth:
    def __init__(self, response: FakeSignInResponse) -> None:
        self.response = response
        self.credentials = None

    async def sign_in_with_password(self, credentials: dict[str, str]) -> FakeSignInResponse:
        self.credentials = credentials
        return self.response


class FakeSupabaseClient:
    def __init__(self, response: FakeSignInResponse) -> None:
        self.auth = FakeAuth(response)


def create_test_client(response: FakeSignInResponse) -> TestClient:
    app = create_app()
    fake_client = FakeSupabaseClient(response)

    async def fake_get_db() -> FakeSupabaseClient:
        return fake_client

    app.dependency_overrides[get_db] = fake_get_db
    return TestClient(app)


def test_signin_returns_supabase_tokens() -> None:
    client = create_test_client(FakeSignInResponse(FakeSession(), FakeUser()))

    response = client.post(
        "/auth/signin",
        json={"email": " jane@example.com ", "password": "password123"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "access_token": "access-token",
        "refresh_token": "refresh-token",
        "token_type": "bearer",
        "user": {
            "id": "18f22a43-64a1-45b6-ad48-257f79d4b4e1",
            "email": "jane@example.com",
        },
    }


def test_signin_requires_supabase_session() -> None:
    client = create_test_client(FakeSignInResponse(None, FakeUser()))

    response = client.post(
        "/auth/signin",
        json={"email": "jane@example.com", "password": "password123"},
    )

    assert response.status_code == 502