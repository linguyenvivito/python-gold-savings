from fastapi import APIRouter
from fastapi import Depends

from src.core.uow import UnitOfWork, get_uow
from .command import CreateUserCommand
from .handler import CreateUserHandler

router = APIRouter()

@router.post("/users")

def create(
    command: CreateUserCommand,
    uow: UnitOfWork = Depends(get_uow)):

    handler = CreateUserHandler()
    return handler.handle(command, uow)