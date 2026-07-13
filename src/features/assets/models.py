from pydantic import BaseModel

class AssetResponse(BaseModel):
  id: int
  sku: str
  product_type: str
  purity: str
  weight: float
  weight_unit: str
  quantity: int