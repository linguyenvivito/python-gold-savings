import time
from supabase import AsyncClient

async def verify_supabase_connectivity(db: AsyncClient) -> tuple[bool, float | None]:
    """
    Executes a feather-light query against a baseline table to ensure
    the API routing, credentials, and database are functional.
    """
    start_time = time.perf_counter()
    try:
        # Testing query execution with a strict limit of 1 row to prevent overhead
        await db.table("users").select("id").limit(1).execute()
        
        end_time = time.perf_counter()
        latency = round((end_time - start_time) * 1000, 2)
        return True, latency
        
    except Exception as e:
        # Print error details to your server terminal console for internal debugging
        print(f"🚨 Supabase Connection Breakdown Check Failed: {str(e)}")
        return False, None