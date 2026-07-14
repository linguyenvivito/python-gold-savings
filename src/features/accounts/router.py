import logging
from typing import Any, cast

from fastapi import APIRouter, Depends, HTTPException, status
from supabase import AsyncClient
from src.core.supabase_connection import get_db

from src.features.accounts.models import AccountResponse, ProfileResponse

router = APIRouter(prefix="/accounts", tags=["accounts"])
logger = logging.getLogger(__name__)

@router.get("/health", status_code=status.HTTP_200_OK)
def health_check():
    return {"status": "ok"}

@router.get("/get", status_code=status.HTTP_200_OK)
def get_accounts() -> list[AccountResponse]:
    # Placeholder for actual account retrieval logic
    accounts = [
        AccountResponse(id="18f22a43-64a1-45b6-ad48-257f79d4b4e1", userId="18f22a43-64a1-45b6-ad48-257f79d4b4e5", assetId="1", quantityAvailable=2, source="SJC")
    ]
    return accounts


@router.get("/profile", response_model=ProfileResponse, status_code=status.HTTP_200_OK)
async def get_account_profile(id: str, db: AsyncClient = Depends(get_db)) -> ProfileResponse:
    response = (
        await db.table("profiles")
        .select("id,user_id,full_name,phone,currency")
        .eq("user_id", id)
        .limit(1)
        .execute()
    )

    if not response.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Profile matching identifier '{id}' was not found.",
        )

    profile = cast(dict[str, Any], response.data[0])
    return ProfileResponse(
        id=str(profile["id"]),
        userId=str(profile.get("user_id") or profile["id"]),
        fullName=profile.get("full_name"),
        currency=profile.get("currency"),
        phoneNumber=profile.get("phone"),
    )