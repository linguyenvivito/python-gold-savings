class GetUserHandler:

    def handle(self, query, uow):

        return uow.users.get(query.id)