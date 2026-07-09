from src.core.database import SessionLocal
from src.infrastructure.repositories.notification_repository import NotificationRepository
from src.infrastructure.repositories.user_repository import UserRepository

class UnitOfWork:

    def __init__(self):

        self.session = SessionLocal()

        self.users = UserRepository(self.session)
        self.notifications = NotificationRepository(self.session)

    def commit(self):

        self.session.commit()

    def rollback(self):

        self.session.rollback()

    def close(self):

        self.session.close()

    def __enter__(self):

        return self

    def __exit__(self, exc_type, exc, tb):

        if exc:

            self.rollback()

        else:

            self.commit()

        self.close()

def get_uow():
    with UnitOfWork() as uow:
        yield uow