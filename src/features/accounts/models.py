from decimal import Decimal
from datetime import datetime
from pydantic import BaseModel

class AccountResponse(BaseModel):
  id: str
  profile_id: str
  account_name: str
  target_amount: Decimal
  target_weight: Decimal
  target_weight_unit: str
  is_active: bool
  created_at: datetime
  updated_at: datetime
  source: str


class ProfileResponse(BaseModel):
  id: str
  userId: str
  fullName: str | None = None
  currency: str | None = "VND"
  phoneNumber: str | None = None


