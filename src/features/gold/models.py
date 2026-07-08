from pydantic import BaseModel
from datetime import datetime

class GoldPrice(BaseModel):
    brand: str
    product: str
    buy: float
    sell: float
    updated_at: datetime