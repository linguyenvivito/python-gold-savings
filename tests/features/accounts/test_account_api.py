from fastapi.testclient import TestClient

from main import create_app
from src.core.supabase_connection import get_db


PROFILE_USER_ID = "18f22a43-64a1-45b6-ad48-257f79d4b4e1"


class FakeSupabaseResponse:
    def __init__(self, data: list[dict[str, str | None]]) -> None:
        self.data = data


class FakeProfileQuery:
    def __init__(self, data: list[dict[str, str | None]], expected_user_id: str) -> None:
        self.data = data
        self.expected_user_id = expected_user_id

    def select(self, columns: str) -> "FakeProfileQuery":
        return self

    def eq(self, column: str, value: str) -> "FakeProfileQuery":
        assert column == "user_id"
        assert value == self.expected_user_id
        return self

    def limit(self, count: int) -> "FakeProfileQuery":
        return self

    async def execute(self) -> FakeSupabaseResponse:
        return FakeSupabaseResponse(self.data)


class FakeSupabaseClient:
    def __init__(self, data: list[dict[str, str | None]], user_id: str) -> None:
        self.data = data
        self.auth = FakeSupabaseAuth(user_id)
        self.postgrest = FakePostgrest()

    def table(self, name: str) -> FakeProfileQuery:
        assert name == "profiles"
        return FakeProfileQuery(self.data, self.auth.user_id)


class FakeSupabaseUser:
    def __init__(self, user_id: str) -> None:
        self.id = user_id


class FakeSupabaseUserResponse:
    def __init__(self, user_id: str) -> None:
        self.user = FakeSupabaseUser(user_id)


class FakeSupabaseAuth:
    def __init__(self, user_id: str) -> None:
        self.user_id = user_id

    async def get_user(self, token: str) -> FakeSupabaseUserResponse:
        assert token == "valid-token"
        return FakeSupabaseUserResponse(self.user_id)


class FakePostgrest:
    def __init__(self) -> None:
        self.token = None

    def auth(self, token: str) -> None:
        assert token == "valid-token"
        self.token = token


def create_test_client_with_profile_data(data: list[dict[str, str | None]], user_id: str = PROFILE_USER_ID) -> TestClient:
    app = create_app()

    async def fake_get_db() -> FakeSupabaseClient:
        return FakeSupabaseClient(data, user_id)

    app.dependency_overrides[get_db] = fake_get_db
    return TestClient(app)


def auth_headers() -> dict[str, str]:
    return {"Authorization": "Bearer valid-token"}

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


def test_account_get_profile() -> None:
    client = create_test_client_with_profile_data([
        {
            "id": PROFILE_USER_ID,
            "user_id": PROFILE_USER_ID,
            "full_name": "Jane Doe",
            "phone": "1234567890",
            "currency": "VND",
        }
    ])

    response = client.get("/accounts/profile", headers=auth_headers())

    assert response.status_code == 200
    assert response.json() == {
        "id": PROFILE_USER_ID,
        "userId": PROFILE_USER_ID,
        "fullName": "Jane Doe",
        "currency": "VND",
        "phoneNumber": "1234567890",
    }


def test_account_get_profile_not_found() -> None:
    client = create_test_client_with_profile_data([])

    response = client.get("/accounts/profile", headers=auth_headers())

    assert response.status_code == 404