"""
Health check routes
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis
from qdrant_client import AsyncQdrantClient

from packages.core.database import get_db
from packages.core.redis import get_redis
from packages.core.qdrant import get_qdrant
from packages.core.config import settings
from packages.core.logging import get_logger

router = APIRouter()
logger = get_logger("health")


@router.get("/")
async def health_root():
    """Basic health check"""
    return {
        "status": "healthy",
        "service": "researchos-api",
        "version": "1.0.0",
    }


@router.get("/ready")
async def readiness_check(
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
    qdrant: AsyncQdrantClient = Depends(get_qdrant),
):
    """Readiness check - verifies all dependencies"""
    checks = {}
    
    # Database
    try:
        await db.execute("SELECT 1")
        checks["database"] = "healthy"
    except Exception as e:
        checks["database"] = f"unhealthy: {e}"
    
    # Redis
    try:
        await redis.ping()
        checks["redis"] = "healthy"
    except Exception as e:
        checks["redis"] = f"unhealthy: {e}"
    
    # Qdrant
    try:
        await qdrant.get_collections()
        checks["qdrant"] = "healthy"
    except Exception as e:
        checks["qdrant"] = f"unhealthy: {e}"
    
    all_healthy = all(v == "healthy" for v in checks.values())
    
    return {
        "status": "ready" if all_healthy else "not_ready",
        "checks": checks,
        "environment": settings.ENVIRONMENT,
    }


@router.get("/live")
async def liveness_check():
    """Liveness check - just confirms process is alive"""
    return {"status": "alive"}


@router.get("/config")
async def config_check():
    """Configuration status (non-sensitive)"""
    return {
        "environment": settings.ENVIRONMENT,
        "free_only": settings.FREE_ONLY,
        "max_spend_aud": settings.MAX_SPEND_AUD,
        "default_currency": settings.DEFAULT_CURRENCY,
        "default_country": settings.DEFAULT_COUNTRY,
        "default_timezone": settings.DEFAULT_TIMEZONE,
        "available_search_providers": settings.available_search_providers,
        "available_ai_providers": settings.available_ai_providers,
        "log_level": settings.LOG_LEVEL,
    }