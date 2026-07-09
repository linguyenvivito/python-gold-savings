from datetime import datetime
from datetime import timezone

from fastapi.testclient import TestClient

from main import create_app
from src.core.uow import get_uow


class FakeScheduled:
    def __init__(self, id, status, scheduled_for):
        self.id = id
        self.status = status
        self.scheduled_for = scheduled_for


class FakeNotification:
    def __init__(self, id, title, message, created_at, read_at=None):
        self.id = id
        self.title = title
        self.message = message
        self.created_at = created_at
        self.read_at = read_at


class FakeNotificationRepository:
    def __init__(self):
        now = datetime.now(timezone.utc)
        self._scheduled_id = 100
        self.notifications_by_user = {
            1: [
                FakeNotification(
                    id=1,
                    title="Welcome",
                    message="Hello",
                    created_at=now,
                    read_at=None,
                )
            ]
        }

    def schedule_broadcast(self, title, message, scheduled_for):
        self._scheduled_id += 1
        return FakeScheduled(self._scheduled_id, "pending", scheduled_for)

    def dispatch_due(self, now_utc):
        return 4

    def list_for_user(self, user_id, unread_only=False, limit=50):
        items = self.notifications_by_user.get(user_id, [])[:limit]
        if unread_only:
            return [item for item in items if item.read_at is None]
        return items

    def mark_as_read(self, user_id, notification_id, read_at):
        items = self.notifications_by_user.get(user_id, [])
        for item in items:
            if item.id == notification_id:
                item.read_at = read_at
                return True
        return False


class FakeUnitOfWork:
    def __init__(self):
        self.notifications = FakeNotificationRepository()


def test_schedule_broadcast_returns_created(monkeypatch):
    monkeypatch.setenv("NOTIFICATION_SCHEDULER_ENABLED", "false")

    app = create_app()
    app.dependency_overrides[get_uow] = lambda: FakeUnitOfWork()

    client = TestClient(app)
    response = client.post(
        "/notifications/schedule",
        json={
            "title": "Gold Alert",
            "message": "Market has changed",
            "scheduled_for": "2030-01-01T08:30:00Z",
        },
    )

    assert response.status_code == 201
    payload = response.json()
    assert payload["status"] == "pending"
    assert payload["id"] >= 101


def test_dispatch_due_returns_created_count(monkeypatch):
    monkeypatch.setenv("NOTIFICATION_SCHEDULER_ENABLED", "false")

    app = create_app()
    app.dependency_overrides[get_uow] = lambda: FakeUnitOfWork()

    client = TestClient(app)
    response = client.post("/notifications/dispatch-due")

    assert response.status_code == 200
    assert response.json() == {"created_notifications": 4}


def test_get_user_notifications_lists_items(monkeypatch):
    monkeypatch.setenv("NOTIFICATION_SCHEDULER_ENABLED", "false")

    app = create_app()
    app.dependency_overrides[get_uow] = lambda: FakeUnitOfWork()

    client = TestClient(app)
    response = client.get("/notifications/users/1")

    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 1
    assert payload[0]["title"] == "Welcome"


def test_mark_notification_as_read_returns_404_when_missing(monkeypatch):
    monkeypatch.setenv("NOTIFICATION_SCHEDULER_ENABLED", "false")

    app = create_app()
    app.dependency_overrides[get_uow] = lambda: FakeUnitOfWork()

    client = TestClient(app)
    response = client.patch("/notifications/users/1/999/read")

    assert response.status_code == 404
