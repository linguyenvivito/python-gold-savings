from pydantic import BaseModel

class AssetResponse(BaseModel):
  id: int
  code: str
  type: str
  unit: str