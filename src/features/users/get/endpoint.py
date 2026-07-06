from fastapi import APIRouter

from .query import GetUserQuery
from .handler import GetUserHandler
from src.core.uow import UnitOfWork

router = APIRouter()

@router.get("/users/{id}")

def get_user(id: int):

    with UnitOfWork() as uow:

        handler = GetUserHandler()

        user = handler.handle(GetUserQuery(id), uow)

        return user