from pydantic import BaseModel

class AccountResponse(BaseModel):
  id: str
  userId: str
  assetId: str
  quantityAvailable: int
  source: str
