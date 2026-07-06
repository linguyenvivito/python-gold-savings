from src.features.users.create.command import CreateUserCommand
from src.features.users.create.handler import CreateUserHandler


class FakeUserRepository:

    def __init__(self):
        self.users = []

    def add(self, user):
        self.users.append(user)

class FakeUnitOfWork:

    def __init__(self):
        self.users = FakeUserRepository()

    def commit(self):
        pass

def test_create_user():

    uow = FakeUnitOfWork()

    handler = CreateUserHandler()

    command = CreateUserCommand(

        username="alice",
        password_hash="hashed-password"
    )

    handler.handle(command, uow)

    assert len(uow.users.users) == 1