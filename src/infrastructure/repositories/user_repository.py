from src.domains.models import User

from src.domains.repositories import IUserRepository


class UserRepository(IUserRepository):

    def __init__(self, session):
        self.session = session

    def add(self, user):

        self.session.add(user)

    def get(self, id):

        return self.session.get(User, id)