from fastapi import APIRouter

router = APIRouter(prefix="/stores", tags=["stores"])

@router.get("/health")
def health_check():
    return {"status": "ok"}

@router.get("/get")
def get_stores():
    # Placeholder for actual store retrieval logic
    stores = [
        {"id": 1, "code": "SJC", "name": "SJC", "image": "https://static.vecteezy.com/system/resources/previews/023/654/784/non_2x/golden-logo-template-free-png.png", "address": "123 Main St", "phone": "123-456-7890", "culture": "vi-VN", "note": "Note A"},
        {"id": 2, "code": "PNJ", "name": "PNJ", "image": "https://static.vecteezy.com/system/resources/previews/023/654/784/non_2x/golden-logo-template-free-png.png", "address": "456 Elm St", "phone": "987-654-3210", "culture": "vi-VN", "note": "Note B"},
    ]
    return stores