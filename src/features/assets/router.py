import logging

from fastapi import APIRouter, status
from supabase_auth import BaseModel

from src.features.assets.models import AssetResponse

class AssetRequest(BaseModel):
    sku: str
    product_type: str
    purity: str
    weight: float
    weight_unit: str
    quantity: int

router = APIRouter(prefix="/assets", tags=["assets"])
logger = logging.getLogger(__name__)

@router.get("/health", status_code=status.HTTP_200_OK)
def health_check():
    return {"status": "ok"}

@router.get("/get", status_code=status.HTTP_200_OK)
def get_assets() -> list[AssetResponse]:
    # Placeholder for actual asset retrieval logic
    assets = [
        AssetResponse(
            id=1, 
            sku="GOLD-RING-24K-001",   # A true unique identifier/code
            product_type="RING",       # Clarifies what the asset physically is
            purity="24k",              # Clear labeling for gold quality
            weight=9999.0,              # A float/decimal for easy math
            weight_unit="mace",        # Explicitly defines what the weight number means
            quantity=1                 # Count of physical items in stock
        ),
        AssetResponse(
            id=2, 
            sku="GOLD-RING-24K-002",   # A true unique identifier/code
            product_type="RING",       # Clarifies what the asset physically is
            purity="24k",              # Clear labeling for gold quality
            weight=999.0,              # A float/decimal for easy math
            weight_unit="mace",        # Explicitly defines what the weight number means
            quantity=1  
        ),
        AssetResponse(
            id=3, 
            sku="GOLD-RING-24K-003",   # A true unique identifier/code
            product_type="RING",       # Clarifies what the asset physically is
            purity="24k",              # Clear labeling for gold quality
            weight=980.0,              # A float/decimal for easy math
            weight_unit="mace",        # Explicitly defines what the weight number means
            quantity=1  
        ),
        AssetResponse(
            id=4, 
            sku="GOLD-RING-23K-004",   # A true unique identifier/code
            product_type="RING",       # Clarifies what the asset physically is
            purity="23k",              # Clear labeling for gold quality
            weight=958.3,              # A float/decimal for easy math
            weight_unit="mace",        # Explicitly defines what the weight number means
            quantity=1  
        ),
        AssetResponse(
            id=5, 
            sku="GOLD-RING-22K-005",   # A true unique identifier/code
            product_type="RING",       # Clarifies what the asset physically is
            purity="22k",              # Clear labeling for gold quality
            weight=916.0,              # A float/decimal for easy math
            weight_unit="mace",        # Explicitly defines what the weight number means
            quantity=1  
        ),
        AssetResponse(
            id=6, 
            sku="GOLD-RING-18K-006",   # A true unique identifier/code
            product_type="RING",       # Clarifies what the asset physically is
            purity="18k",              # Clear labeling for gold quality
            weight=750.0,              # A float/decimal for easy math
            weight_unit="mace",        # Explicitly defines what the weight number means
            quantity=1  
        ),
        AssetResponse(
            id=7,
            sku="GOLD-RING-14K-007",   # A true unique identifier/code
            product_type="RING",       # Clarifies what the asset physically is
            purity="14k",              # Clear labeling for gold quality
            weight=585.0,              # A float/decimal for easy math
            weight_unit="mace",        # Explicitly defines what the weight number means
            quantity=1  
        )
    ]
    return assets