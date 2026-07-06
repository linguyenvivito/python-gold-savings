from pydantic import BaseModel


class CreateUserCommand(BaseModel):

    username: str

    password_hash: str