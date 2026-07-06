from src.domains.models import User

from src.domains.repositories import IAuditRepository


class AuditRepository(IAuditRepository):

    def __init__(self, session):
        self.session = session

    def add(self, audit_event):

        self.session.add(audit_event)

    def get(self, id):

        return self.session.get(User, id)