import os
from dotenv import load_dotenv
from supabase import AsyncClient, acreate_client

# Load environment variables from .env
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL") or ""
SUPABASE_KEY = os.getenv("SUPABASE_KEY") or ""

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Missing SUPABASE_URL or SUPABASE_KEY in environment variables.")

# Shared variable holding our active client state
_supabase_client: AsyncClient | None = None

async def init_supabase() -> AsyncClient:
    """Instantiates the asynchronous client singleton on application start."""
    global _supabase_client
    if _supabase_client is None:
        _supabase_client = await acreate_client(SUPABASE_URL, SUPABASE_KEY)
    return _supabase_client

async def get_db() -> AsyncClient:
    """Dependency injector yielding the database client to features."""
    if _supabase_client is None:
        raise RuntimeError("Supabase client is not initialized. Call init_supabase() first.")
    return _supabase_client