from pydantic import BaseModel

class OrderResponse(BaseModel):
    id: int
    userId: str
    assetId: int
    side: str
    quantity: int
    price: int
    otherPrice: int
    createdAt: str

