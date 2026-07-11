from fastapi import HTTPException, status
from supabase import Client
from typing import Any, cast

def query_supabase_user_by_id(db: Client, user_id: str) -> dict[str, Any]:
    """Executes the raw database selection routine against the users table."""
    try:
        response = (
            db.table("users")
            .select("*")
            .execute()
        )
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User profile matching identifier '{user_id}' was not found."
            )
            
        return cast(dict[str, Any], response.data[0])
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database operational failure: {str(e)}"
        )