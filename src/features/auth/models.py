from pydantic import BaseModel, Field, field_validator

from src.core.sanitization import sanitize_text


class RegisterRequest(BaseModel):
    email: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6, max_length=128)

    @field_validator("email", mode="before")
    @classmethod
    def sanitize_email(cls, value: str) -> str:
        return sanitize_text(value)


class LoginRequest(BaseModel):
    email: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6, max_length=128)

    @field_validator("email", mode="before")
    @classmethod
    def sanitize_email(cls, value: str) -> str:
        return sanitize_text(value)


class UserResponse(BaseModel):
    id: str
    email: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str = Field(..., min_length=1)


class RevokeTokenRequest(BaseModel):
    refresh_token: str = Field(..., min_length=1)


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserResponse


class AnonymousAuthUserResponse(BaseModel):
    id: str
    is_anonymous: bool | None = None


class AnonymousAuthResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int | None = None
    expires_at: int | None = None
    user: AnonymousAuthUserResponse
