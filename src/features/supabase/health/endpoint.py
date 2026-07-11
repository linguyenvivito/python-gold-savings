from fastapi import APIRouter, Depends, HTTPException, status
from supabase import AsyncClient
from src.core.supabase_connection import get_db
from ..models import HealthCheckResponse
from .handler import verify_supabase_connectivity

router = APIRouter(prefix="/supabase/health", tags=["Supabase"])

@router.get("", response_model=HealthCheckResponse)
async def perform_system_health_check(db: AsyncClient = Depends(get_db)):
    """
    Evaluates whole-system operational statuses including downstream database connections.
    """
    try:
        is_db_healthy, latency = await verify_supabase_connectivity(db)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "status": "unhealthy",
                "database_connected": False,
                "latency_ms": None,
                "error": str(exc),
            },
        ) from exc
    
    if not is_db_healthy:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "status": "unhealthy", 
                "database_connected": False, 
                "latency_ms": None,
                "error": "Supabase connectivity check failed.",
            }
        )
        
    return HealthCheckResponse(
        status="healthy",
        database_connected=True,
        latency_ms=latency
    )