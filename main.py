from contextlib import asynccontextmanager
import os
import logging
from time import time
from typing import Any, Dict

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from src.core.supabase_connection import init_supabase
from src.core.logging_config import configure_logging
from src.core.database import get_connection
from src.core.rate_limit import limiter
from src.middleware.cors_restriction import CorsRestrictionMiddleware
from src.middleware.csrf_protection import CsrfProtectionMiddleware
from src.middleware.request_logging import RequestLoggingMiddleware
from src.middleware.request_metrics import RequestMetricsMiddleware
from src.middleware.security_headers import SecurityHeadersMiddleware

# Store router
from src.features.stores.get.endpoint import router as stores_get_router

from src.features.assets.router import router as assets_router

from src.features.transaction.router import router as orders_router
from src.features.accounts.router import router as accounts_router
from src.features.users.create.endpoint import router as user_create_router
from src.features.users.get.endpoint import router as user_get_router
from src.features.notifications.router import router as notifications_router
from src.features.notifications.scheduler import is_scheduler_enabled
from src.features.notifications.scheduler import scheduler
from src.features.ai.router import router as ai_router

from src.features.gold.router import router as gold_router
from src.features.gold.pnj.router import router as gold_pnj_router
from src.features.gold.sjc.router import router as gold_sjc_router
from src.features.gold.doji.router import router as gold_doji_router
from src.features.gold.kimmon.router import router as gold_kimmon_router
from src.features.gold.mihong.router import router as gold_mihong_router
from src.features.gold.baotinmanhhai.router import router as gold_baotinmanhhai_router
from src.features.gold.baotinminhchau.router import router as gold_baotinminhchau_router

from src.features.supabase.health.endpoint import router as health_router # <-- Import Health
from src.features.auth.anonymous.endpoint import router as anonymous_auth_router

logger = logging.getLogger("app.security.rate_limit")
APP_STARTED_AT = time()

def _handle_rate_limit_exceeded(request: Request, exc: Exception) -> Response:
    if isinstance(exc, RateLimitExceeded):
        client_host = request.client.host if request.client else "unknown"
        logger.warning(
            "rate limit exceeded method=%s path=%s client=%s",
            request.method,
            request.url.path,
            client_host,
        )
        return _rate_limit_exceeded_handler(request, exc)
    raise exc


def create_app() -> FastAPI:
    configure_logging()

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        """Handles global startup hooks securely before routing traffic."""
        print("🤖 Booting application environment clusters...")
        # Initialize connection singleton pools safely
        await init_supabase()
        yield
        print("🔌 Gracefully closing database pool nodes.")

    app = FastAPI(
        title="Task Management API",
        version="1.0.0",
        lifespan=lifespan
        )
    
    app.state.limiter = limiter

    app.add_exception_handler(RateLimitExceeded, _handle_rate_limit_exceeded)

    @app.get("/health")
    def health_check() -> Dict[str, Any]:
        return {
            "status": "ok",
            "uptime_seconds": int(max(0, time() - APP_STARTED_AT)),
        }

    @app.get("/ready")
    def readiness_check() -> JSONResponse:
        readiness_check_database = (
            os.getenv("READINESS_CHECK_DATABASE", "true").strip().lower() == "true"
        )

        checks: Dict[str, str] = {"database": "skipped"}
        status_code = 200

        if readiness_check_database:
            try:
                with get_connection() as connection:
                    cursor = connection.cursor()
                    try:
                        cursor.execute("SELECT 1")
                    finally:
                        cursor.close()
            except Exception:
                checks["database"] = "error"
                status_code = 503
            else:
                checks["database"] = "ok"

        payload = {
            "status": "ready" if status_code == 200 else "not_ready",
            "checks": checks,
        }
        return JSONResponse(content=payload, status_code=status_code)

    @app.get("/metrics", include_in_schema=False)
    def metrics() -> Response:
        metrics_enabled = os.getenv("METRICS_ENABLED", "true").strip().lower() == "true"
        if not metrics_enabled:
            return Response(status_code=404)
        return Response(content=generate_latest().decode("utf-8"), media_type=CONTENT_TYPE_LATEST)

    @app.on_event("startup")
    async def start_notification_scheduler() -> None:
        if is_scheduler_enabled():
            scheduler.start()

    @app.on_event("shutdown")
    async def stop_notification_scheduler() -> None:
        await scheduler.stop()

    cors_allow_origins = os.getenv(
        "CORS_ALLOW_ORIGINS",
        "*",
    )
    allow_origins = [origin.strip() for origin in cors_allow_origins.split(",") if origin.strip()]

    csrf_trusted_origins = os.getenv("CSRF_TRUSTED_ORIGINS", cors_allow_origins)
    trusted_origins = [origin.strip() for origin in csrf_trusted_origins.split(",") if origin.strip()]

    csrf_enabled = os.getenv("CSRF_ENABLED", "true").strip().lower() == "true"
    csrf_cookie_based_only = (
        os.getenv("CSRF_COOKIE_BASED_ONLY", "true").strip().lower() == "true"
    )
    security_headers_enabled = (
        os.getenv("SECURITY_HEADERS_ENABLED", "true").strip().lower() == "true"
    )
    security_hsts_enabled = (
        os.getenv("SECURITY_HSTS_ENABLED", "true").strip().lower() == "true"
    )
    request_logging_enabled = (
        os.getenv("REQUEST_LOGGING_ENABLED", "true").strip().lower() == "true"
    )
    trace_enabled = os.getenv("TRACE_ENABLED", "false").strip().lower() == "true"
    metrics_enabled = os.getenv("METRICS_ENABLED", "true").strip().lower() == "true"
    strict_origin_check = os.getenv("CORS_STRICT_ORIGIN_CHECK", "true").strip().lower() == "true"

    app.add_middleware(
        RequestLoggingMiddleware,
        enabled=request_logging_enabled,
        trace_enabled=trace_enabled,
    )

    app.add_middleware(
        RequestMetricsMiddleware,
        enabled=metrics_enabled,
    )

    app.add_middleware(
        SecurityHeadersMiddleware,
        enabled=security_headers_enabled,
        hsts_enabled=security_hsts_enabled,
    )

    app.add_middleware(
        CsrfProtectionMiddleware,
        trusted_origins=trusted_origins,
        enabled=csrf_enabled,
        cookie_based_only=csrf_cookie_based_only,
    )

    app.add_middleware(
        CorsRestrictionMiddleware,
        allow_origins=allow_origins,
        strict=strict_origin_check,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=allow_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    app.add_middleware(SlowAPIMiddleware)
    app.include_router(user_create_router)
    app.include_router(user_get_router)
    app.include_router(notifications_router)
    app.include_router(ai_router)
    app.include_router(orders_router)
    app.include_router(accounts_router)
    app.include_router(stores_get_router)
    app.include_router(gold_router)
    app.include_router(gold_pnj_router)
    app.include_router(gold_sjc_router)
    app.include_router(gold_doji_router)
    app.include_router(gold_kimmon_router)
    app.include_router(gold_mihong_router)
    app.include_router(gold_baotinmanhhai_router)
    app.include_router(gold_baotinminhchau_router)
    app.include_router(health_router)  # <-- Include Health router
    app.include_router(anonymous_auth_router)

    app.include_router(assets_router)  # <-- Include Assets router

    return app

app = create_app()
