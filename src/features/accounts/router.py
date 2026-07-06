import logging

from fastapi import APIRouter, status

from src.features.accounts.models import AccountResponse

router = APIRouter(prefix="/accounts", tags=["accounts"])
logger = logging.getLogger(__name__)

@router.get("/health", status_code=status.HTTP_200_OK)
def health_check():
    return {"status": "ok"}

@router.get("/get", status_code=status.HTTP_200_OK)
def get_accounts() -> list[AccountResponse]:
    # Placeholder for actual account retrieval logic
    accounts = [
        AccountResponse(id="18f22a43-64a1-45b6-ad48-257f79d4b4e1", userId="18f22a43-64a1-45b6-ad48-257f79d4b4e5", assetId="1", quantityAvailable=2, source="SJC")
    ]
    return accounts