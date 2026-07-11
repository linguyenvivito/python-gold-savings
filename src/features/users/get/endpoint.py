from fastapi import APIRouter, Depends
from supabase import Client
from src.core.supabase_connection import get_db

from .query import GetUserByIdQuery, GetUserByIdHandler
from ..models import UserResponse

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/{user_id}", response_model=UserResponse)
def get_user_by_id_endpoint(
    user_id: str, 
    db: Client = Depends(get_db)
):
    """Endpoint intercepting incoming mobile requests to dispatch the query handler."""
    # Instantiating the feature query worker
    handler = GetUserByIdHandler(db_client=db)
    
    # Executing the handler by feeding it the query record parameters
    user_profile = handler.handle(GetUserByIdQuery(user_id=user_id))
    
    return user_profile