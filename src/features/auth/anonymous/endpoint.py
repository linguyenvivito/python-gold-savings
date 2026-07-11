from fastapi import APIRouter, Depends, HTTPException, status
from supabase import AsyncClient
from src.core.supabase_connection import get_db

from ..models import AnonymousAuthResponse, AnonymousAuthUserResponse


router = APIRouter(prefix="/auth/anonymous", tags=["auth"])

@router.post("", response_model=AnonymousAuthResponse, status_code=status.HTTP_201_CREATED)
async def sign_in_anonymously_endpoint(
    db: AsyncClient = Depends(get_db),
) -> AnonymousAuthResponse:
    try:
        response = await db.auth.sign_in_anonymously(
            {"options": {"captcha_token": ""}}
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Supabase anonymous sign-in failed: {str(exc)}",
        ) from exc

    if response.session is None or response.user is None:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Supabase anonymous sign-in did not return a session.",
        )

    return AnonymousAuthResponse(
        access_token=response.session.access_token,
        refresh_token=response.session.refresh_token,
        token_type=response.session.token_type,
        expires_in=response.session.expires_in,
        expires_at=response.session.expires_at,
        user=AnonymousAuthUserResponse(
            id=response.user.id,
            is_anonymous=response.user.is_anonymous,
        ),
    )