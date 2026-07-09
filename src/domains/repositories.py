from abc import ABC
from abc import abstractmethod


class IAuditRepository(ABC):

    @abstractmethod
    def get(self, id):
        pass

class IUserRepository(ABC):

    @abstractmethod
    def add(self, user):
        pass

    @abstractmethod
    def get(self, id):
        pass


class INotificationRepository(ABC):

    @abstractmethod
    def schedule_broadcast(self, title, message, scheduled_for):
        pass

    @abstractmethod
    def dispatch_due(self, now_utc):
        pass

    @abstractmethod
    def list_for_user(self, user_id, unread_only=False, limit=50):
        pass

    @abstractmethod
    def mark_as_read(self, user_id, notification_id, read_at):
        pass

    @abstractmethod
    def register_push_token(self, user_id, provider, token):
        pass