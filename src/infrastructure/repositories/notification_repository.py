from datetime import datetime, timezone

from sqlalchemy import select

from src.domains.models import Notification
from src.domains.models import NotificationPushToken
from src.domains.models import ScheduledNotification
from src.domains.models import User
from src.domains.repositories import INotificationRepository


class NotificationRepository(INotificationRepository):

    def __init__(self, session):
        self.session = session

    def schedule_broadcast(self, title, message, scheduled_for):
        scheduled = ScheduledNotification(
            title=title,
            message=message,
            scheduled_for=scheduled_for,
            status="pending",
        )
        self.session.add(scheduled)
        self.session.flush()
        return scheduled

    def dispatch_due(self, now_utc):
        due_notifications = self.session.execute(
            select(ScheduledNotification).where(
                ScheduledNotification.status == "pending",
                ScheduledNotification.scheduled_for <= now_utc,
            )
        ).scalars().all()

        if not due_notifications:
            return 0

        user_ids = self.session.execute(select(User.id)).scalars().all()

        created_count = 0
        for scheduled in due_notifications:
            for user_id in user_ids:
                self.session.add(
                    Notification(
                        user_id=user_id,
                        title=scheduled.title,
                        message=scheduled.message,
                        scheduled_notification_id=scheduled.id,
                    )
                )
                created_count += 1

            scheduled.status = "dispatched"
            scheduled.dispatched_at = now_utc

        self.session.flush()
        return created_count

    def list_for_user(self, user_id, unread_only=False, limit=50):
        statement = (
            select(Notification)
            .where(Notification.user_id == user_id)
            .order_by(Notification.created_at.desc())
            .limit(limit)
        )

        if unread_only:
            statement = statement.where(Notification.read_at.is_(None))

        return self.session.execute(statement).scalars().all()

    def mark_as_read(self, user_id, notification_id, read_at):
        notification = self.session.get(Notification, notification_id)
        if notification is None or notification.user_id != user_id:
            return False

        if notification.read_at is None:
            notification.read_at = read_at or datetime.now(timezone.utc)
            self.session.flush()

        return True

    def register_push_token(self, user_id, provider, token):
        user = self.session.get(User, user_id)
        if user is None:
            return False

        existing_token = self.session.execute(
            select(NotificationPushToken).where(NotificationPushToken.token == token)
        ).scalar_one_or_none()

        if existing_token is not None:
            existing_token.user_id = user_id
            existing_token.provider = provider
            self.session.flush()
            return True

        self.session.add(
            NotificationPushToken(
                user_id=user_id,
                provider=provider,
                token=token,
            )
        )
        self.session.flush()
        return True
