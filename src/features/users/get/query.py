from typing import NamedTuple
from supabase import Client
from .handler import query_supabase_user_by_id

# ==========================================
# 1. READ / QUERY DATA STRUCTURES (Immutable)
# ==========================================
class GetUserByIdQuery(NamedTuple):
    """Immutable data record carrying request context parameters."""
    user_id: str


# ==========================================
# 2. THE QUERY HANDLER
# ==========================================
class GetUserByIdHandler:
    """Coordinates and manages execution data fetching operations."""
    def __init__(self, db_client: Client):
        self.db = db_client

    def handle(self, query: GetUserByIdQuery) -> dict:
        """Processes the query by invoking the database service layer."""
        return query_supabase_user_by_id(db=self.db, user_id=query.user_id)