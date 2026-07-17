import logging
from typing import Any, cast

from fastapi import APIRouter, Depends, HTTPException, status
from supabase import AsyncClient
from src.features.auth.models import LoginRequest, TokenResponse, UserResponse
from src.core.supabase_connection import get_db

router = APIRouter(prefix="/auth", tags=["auth"])
logger = logging.getLogger(__name__)

@router.get("/health", status_code=status.HTTP_200_OK)
def health_check():
    return {"status": "ok"}

@router.post("/signin", response_model=TokenResponse, status_code=status.HTTP_200_OK)
async def signin(login_request: LoginRequest, db: AsyncClient = Depends(get_db)) -> TokenResponse:
    try:
        response = await db.auth.sign_in_with_password(
            {"email": login_request.email, "password": login_request.password}
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Supabase sign-in failed: {str(exc)}",
        ) from exc
    if response.session is None or response.user is None:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Supabase sign-in did not return a session.",
        )
    user = cast(Any, response.user)
    session = cast(Any, response.session)
    return TokenResponse(
        access_token=session.access_token,
        refresh_token=session.refresh_token,
        token_type=session.token_type,
        user=UserResponse(
            id=user.id,
            email=user.email,
        ),
    )


