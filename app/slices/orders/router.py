from fastapi import APIRouter, Depends, HTTPException, status

from app.slices.orders.models import OrderResponse

router = APIRouter(prefix="/orders", tags=["orders"])

@router.get("/health", status_code=status.HTTP_200_OK)
def health_check():
    return {"status": "ok"}


@router.get("/get", status_code=status.HTTP_200_OK)
def get_orders() -> list[OrderResponse]:
    # Placeholder for actual order retrieval logic
    orders = [
        OrderResponse(id=1, userId="18f22a43-64a1-45b6-ad48-257f79d4b4e5", assetId=1, side="BUY", quantity=1, price=14000000, otherPrice=0, createdAt="2024-06-01T00:00:00Z"), 
        OrderResponse(id=2, userId="18f22a43-64a1-45b6-ad48-257f79d4b4e5", assetId=2, side="BUY", quantity=1, price=14000000, otherPrice=0, createdAt="2024-06-01T00:00:00Z")
    ]
    return orders