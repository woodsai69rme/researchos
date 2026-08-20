"""
Settings routes - User and system settings
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from uuid import UUID

from packages.core.database import get_db
from packages.core.config import settings
from packages.core.logging import get_logger
from packages.core.security import free_policy_engine, FreePolicyMode

router = APIRouter()
logger = get_logger("settings")


class SettingsResponse(BaseModel):
    free_only: bool
    max_spend_aud: float
    default_currency: str
    default_country: str
    default_timezone: str
    policy_mode: str
    available_search_providers: List[str]
    available_ai_providers: List[str]


class PolicyModeRequest(BaseModel):
    mode: str = Field(..., pattern="^(FREE_ONLY|FREE_FIRST|CHEAP|FULL)$")


@router.get("/", response_model=SettingsResponse)
async def get_settings():
    """Get current settings"""
    return SettingsResponse(
        free_only=settings.FREE_ONLY,
        max_spend_aud=settings.MAX_SPEND_AUD,
        default_currency=settings.DEFAULT_CURRENCY,
        default_country=settings.DEFAULT_COUNTRY,
        default_timezone=settings.DEFAULT_TIMEZONE,
        policy_mode=free_policy_engine.mode.value,
        available_search_providers=settings.available_search_providers,
        available_ai_providers=settings.available_ai_providers,
    )


@router.post("/policy-mode")
async def set_policy_mode(request: PolicyModeRequest):
    """Set free policy mode"""
    try:
        mode = FreePolicyMode(request.mode)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid mode: {request.mode}")
    
    free_policy_engine.set_mode(mode)
    
    return {"success": True, "mode": mode.value}


@router.get("/policy/status")
async def get_policy_status():
    """Get detailed policy status"""
    return free_policy_engine.get_status()


@router.post("/policy/reset-spending")
async def reset_spending():
    """Reset spending counters"""
    free_policy_engine.reset_spending()
    return {"success": True, "message": "Spending counters reset"}


@router.get("/environment")
async def get_environment():
    """Get environment info (non-sensitive)"""
    return {
        "environment": settings.ENVIRONMENT,
        "log_level": settings.LOG_LEVEL,
        "database_configured": bool(settings.DATABASE_URL),
        "redis_configured": bool(settings.REDIS_URL),
        "qdrant_configured": bool(settings.QDRANT_URL),
        "providers_configured": {
            "gemini": bool(settings.GEMINI_API_KEY),
            "openrouter": bool(settings.OPENROUTER_API_KEY),
            "brave": bool(settings.BRAVE_API_KEY),
            "tavily": bool(settings.TAVILY_API_KEY),
            "exa": bool(settings.EXA_API_KEY),
            "serper": bool(settings.SERPER_API_KEY),
            "serpapi": bool(settings.SERPAPI_API_KEY),
            "github": bool(settings.GITHUB_TOKEN),
            "youtube": bool(settings.YOUTUBE_API_KEY),
        },
    }