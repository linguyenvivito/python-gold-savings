from fastapi import APIRouter, Depends, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from supabase import AsyncClient
from src.core.supabase_connection import get_db

security = HTTPBearer()

router = APIRouter(prefix="/gold", tags=["gold"])

@router.get("/health", status_code=status.HTTP_200_OK)
def health_check():
    return {"status": "ok"}

@router.get("/price", status_code=status.HTTP_200_OK)
async def get_gold_prices(credentials: HTTPAuthorizationCredentials = Depends(security), db: AsyncClient = Depends(get_db)):
    user_jwt = credentials.credentials
    
    db.postgrest.auth(user_jwt)

    response = (
        await db.table("gold_prices")
        .select("id, store_id, gold_product_id, buy_price, sell_price, created_at, stores(id, name), gold_products(id, sku, brand, product_name, product_type, purity, weight, weight_unit)")
        .execute()
    )
    
    # The data is accessible via response.data
    return response.data