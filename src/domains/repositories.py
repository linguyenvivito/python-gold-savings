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