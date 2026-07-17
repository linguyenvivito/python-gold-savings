from fastapi import APIRouter, Depends, security, status
from supabase import AsyncClient
from src.features.transaction.models import TransactionResponse
from src.core.supabase_connection import get_db
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

security = HTTPBearer()

router = APIRouter(prefix="/transactions", tags=["transactions"])

@router.get("/health", status_code=status.HTTP_200_OK)
def health_check():
    return {"status": "ok"}

@router.get("", status_code=status.HTTP_200_OK)
async def get_transactions(credentials: HTTPAuthorizationCredentials = Depends(security), db: AsyncClient = Depends(get_db)):
    user_jwt = credentials.credentials
    
    db.postgrest.auth(user_jwt)

    response = (
        await db.table("transactions")
        .select("id")
        .execute()
    )
    
    # The data is accessible via response.data
    return response.data