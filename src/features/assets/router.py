import logging

from fastapi import APIRouter, status

from src.features.assets.models import AssetResponse

router = APIRouter(prefix="/assets", tags=["assets"])
logger = logging.getLogger(__name__)

@router.get("/health", status_code=status.HTTP_200_OK)
def health_check():
    return {"status": "ok"}

@router.get("/get", status_code=status.HTTP_200_OK)
def get_assets() -> list[AssetResponse]:
    # Placeholder for actual asset retrieval logic
    assets = [
        AssetResponse(id=1, code="XAU_24K", type="RING", unit="mace"),
        AssetResponse(id=2, code="XAU_9999", type="BAR", unit="mace"),
    ]
    return assets