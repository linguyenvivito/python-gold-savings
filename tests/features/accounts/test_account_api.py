from fastapi.testclient import TestClient

from main import create_app
from src.core.supabase_connection import get_db


class FakeSupabaseResponse:
    def __init__(self, data: list[dict[str, str | None]]) -> None:
        self.data = data


class FakeProfileQuery:
    def __init__(self, data: list[dict[str, str | None]]) -> None:
        self.data = data

    def select(self, columns: str) -> "FakeProfileQuery":
        return self

    def eq(self, column: str, value: str) -> "FakeProfileQuery":
        return self

    def limit(self, count: int) -> "FakeProfileQuery":
        return self

    async def execute(self) -> FakeSupabaseResponse:
        return FakeSupabaseResponse(self.data)


class FakeSupabaseClient:
    def __init__(self, data: list[dict[str, str | None]]) -> None:
        self.data = data

    def table(self, name: str) -> FakeProfileQuery:
        assert name == "profiles"
        return FakeProfileQuery(self.data)


def create_test_client_with_profile_data(data: list[dict[str, str | None]]) -> TestClient:
    app = create_app()

    async def fake_get_db() -> FakeSupabaseClient:
        return FakeSupabaseClient(data)

    app.dependency_overrides[get_db] = fake_get_db
    return TestClient(app)

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
            "id": "18f22a43-64a1-45b6-ad48-257f79d4b4e1",
            "user_id": "18f22a43-64a1-45b6-ad48-257f79d4b4e1",
            "full_name": "Jane Doe",
            "phone": "1234567890",
            "currency": "VND",
        }
    ])

    response = client.get("/accounts/profile", params={"id": "18f22a43-64a1-45b6-ad48-257f79d4b4e1"})

    assert response.status_code == 200
    assert response.json() == {
        "id": "18f22a43-64a1-45b6-ad48-257f79d4b4e1",
        "userId": "18f22a43-64a1-45b6-ad48-257f79d4b4e1",
        "fullName": "Jane Doe",
        "currency": "VND",
        "phoneNumber": "1234567890",
    }


def test_account_get_profile_not_found() -> None:
    client = create_test_client_with_profile_data([])

    response = client.get("/accounts/profile", params={"id": "missing"})

    assert response.status_code == 404