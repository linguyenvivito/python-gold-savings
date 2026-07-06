from src.domains.models import User


class CreateUserHandler:

    def handle(self, command, uow):

        user = User(

            username=command.username,

            password_hash=command.password_hash
        )

        uow.users.add(user)

        return user