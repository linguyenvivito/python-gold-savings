from fastapi import APIRouter

router = APIRouter(prefix="/stores", tags=["stores"])

@router.get("/health")
def health_check():
    return {"status": "ok"}

# Get all stores
@router.get("/get")
def get_stores():
    stores = [
        {"id": 1, "code": "SJC", "name": "SJC", "image": "https://static.vecteezy.com/system/resources/previews/023/654/784/non_2x/golden-logo-template-free-png.png", "address": "123 Main St", "phone": "123-456-7890", "culture": "vi-VN", "note": "Note A"},
        {"id": 2, "code": "PNJ", "name": "PNJ", "image": "https://static.vecteezy.com/system/resources/previews/023/654/784/non_2x/golden-logo-template-free-png.png", "address": "456 Elm St", "phone": "987-654-3210", "culture": "vi-VN", "note": "Note B"},
    ]
    return stores

# Stores are subscribed by users (Favourite Stores)
@router.get("/favourites")
def get_favourite_stores():
    favourite_stores = [
        {"id": 1, "code": "PNJ", "name": "PNJ", "image": "", "address": "123 Main St", "phone": "123-456-7890", "culture": "vi-VN", "note": "Note A", "userId": "702d1b35-a717-4a3e-a979-5a0fa3e20e15"},
    ]
    return favourite_stores

# Stores are exchanged by users
@router.get("/transactions")
def get_transactions():
    transactions = [
        {"id": 1, "code": "Kim_Mon", "name": "Kim Mon", "image": "", "address": "123 Main St", "phone": "123-456-7890", "culture": "vi-VN", "note": "Note A", "userId": "702d1b35-a717-4a3e-a979-5a0fa3e20e15"},
    ]
    return transactions