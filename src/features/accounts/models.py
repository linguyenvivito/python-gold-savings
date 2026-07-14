from pydantic import BaseModel

class AccountResponse(BaseModel):
  id: str
  userId: str
  assetId: str
  quantityAvailable: int
  source: str


class ProfileResponse(BaseModel):
  id: str
  userId: str
  fullName: str | None = None
  currency: str | None = "VND"
  phoneNumber: str | None = None