import logging
from datetime import datetime, timezone
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from supabase import AsyncClient
from src.core.supabase_connection import get_db

from src.features.accounts.models import AccountResponse

security = HTTPBearer()

router = APIRouter(prefix="/auth/profile", tags=["auth"])
logger = logging.getLogger(__name__)

@router.get("/health", status_code=status.HTTP_200_OK)
def health_check():
    return {"status": "ok"}

@router.get("/test", status_code=status.HTTP_200_OK)
def get_accounts() -> list[AccountResponse]:
    # Placeholder for actual account retrieval logic
    accounts = [
        AccountResponse(
            id="18f22a43-64a1-45b6-ad48-257f79d4b4e1",
            profile_id="18f22a43-64a1-45b6-ad48-257f79d4b4e5",
            account_name="Test Account",
            target_amount=Decimal("1000.00"),
            target_weight=Decimal("50.0"),
            target_weight_unit="grams",
            is_active=True,
            created_at=datetime(2024, 1, 1, tzinfo=timezone.utc),
            updated_at=datetime(2024, 1, 2, tzinfo=timezone.utc),
            source="SJC"    
        )
    ]
    return accounts

@router.get("", status_code=status.HTTP_200_OK)
async def get_profile(credentials: HTTPAuthorizationCredentials = Depends(security), db: AsyncClient = Depends(get_db)):
    user_jwt = credentials.credentials

    try:
        user_response = await db.auth.get_user(user_jwt)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token.",
        ) from exc

    if user_response is None or user_response.user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token.",
        )
    user = user_response.user

    db.postgrest.auth(user_jwt)

    response = (
        await db.table("profiles")
        .select("id, full_name, phone, created_at, updated_at, favourite_stores(id, stores(id, name, address, phone, city, email, website, latitude, longitude, opening_time, closing_time, active, created_at, updated_at)), gold_accounts(id, account_name, target_amount, target_weight, target_weight_unit, transactions(id, transaction_type, quantity, executed_price, cash_amount, fee, note, created_at, gold_product(id, product_name, product_type, purity, weight, weight_unit), stores(id, name, address, phone, city, email, website, latitude, longitude, opening_time, closing_time, active, created_at, updated_at)))")
        .eq("user_id", user.id)
        .execute()
    )
    
    # The data is accessible via response.data
    return response.data

