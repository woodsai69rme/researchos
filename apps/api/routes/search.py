"""
Search routes - Search provider management and execution
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from uuid import UUID

from packages.core.database import get_db
from packages.core.config import settings
from packages.core.logging import get_logger
from packages.core.security import free_policy_engine

router = APIRouter()
logger = get_logger("search")


# ============================================================
# REQUEST/RESPONSE MODELS
# ============================================================

class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=500)
    provider: str = Field(..., description="Search provider to use")
    parameters: Optional[Dict[str, Any]] = Field(None, description="Provider-specific parameters")
    run_id: Optional[UUID] = Field(None, description="Associate with research run")


class SearchResultItem(BaseModel):
    url: str
    title: Optional[str]
    snippet: Optional[str]
    content: Optional[str]
    source_type: Optional[str]
    relevance_score: Optional[float]
    metadata: Optional[Dict[str, Any]]


class SearchResponse(BaseModel):
    search_id: UUID
    provider: str
    query: str
    results: List[SearchResultItem]
    results_count: int
    latency_ms: int
    cost_aud: float


class ProviderInfo(BaseModel):
    name: str
    display_name: str
    provider_type: str
    status: str
    is_free: bool
    free_quota: Optional[int]
    free_quota_reset_period: Optional[str]
    capabilities: Optional[List[str]]
    rate_limit_rpm: Optional[int]
    last_verified: Optional[str]
    is_enabled: bool
    priority: int


# ============================================================
# SEARCH ENDPOINTS
# ============================================================

@router.post("/execute", response_model=SearchResponse)
async def execute_search(
    request: SearchRequest,
    db: AsyncSession = Depends(get_db),
):
    """Execute a search using specified provider"""
    
    # Check if provider is allowed
    allowed, reason = free_policy_engine.can_execute(request.provider, 0)
    if not allowed:
        raise HTTPException(status_code=403, detail=f"Provider not allowed: {reason}")
    
    # TODO: Implement actual search provider execution
    # For now, return mock response
    
    from packages.core.database import get_db_context
    from packages.core.models import Search, SearchResult
    import uuid
    import time
    
    start_time = time.time()
    
    # Create search record
    search = Search(
        run_id=request.run_id,
        provider=request.provider,
        query=request.query,
        parameters=request.parameters,
        status="completed",
        results_count=0,
        cost_aud=0,
        latency_ms=0,
    )
    
    async with get_db_context() as db:
        db.add(search)
        await db.commit()
        await db.refresh(search)
        
        latency_ms = int((time.time() - start_time) * 1000)
        search.latency_ms = latency_ms
        await db.commit()
    
    # Mock results
    mock_results = [
        SearchResultItem(
            url="https://example.com/result1",
            title=f"Result for {request.query}",
            snippet=f"This is a sample result for query: {request.query}",
            source_type="web",
            relevance_score=0.9,
            metadata={"provider": request.provider},
        )
    ]
    
    return SearchResponse(
        search_id=search.id,
        provider=request.provider,
        query=request.query,
        results=mock_results,
        results_count=len(mock_results),
        latency_ms=latency_ms,
        cost_aud=0,
    )


@router.get("/providers", response_model=List[ProviderInfo])
async def list_providers():
    """List all configured search providers"""
    from packages.core.models import Provider, ProviderType, ProviderStatus
    from packages.core.database import get_db_context
    from sqlalchemy import select
    
    async with get_db_context() as db:
        result = await db.execute(
            select(Provider).where(Provider.provider_type == ProviderType.SEARCH)
        )
        providers = result.scalars().all()
    
    return [
        ProviderInfo(
            name=p.name,
            display_name=p.display_name,
            provider_type=p.provider_type.value,
            status=p.status.value,
            is_free=p.is_free,
            free_quota=p.free_quota,
            free_quota_reset_period=p.free_quota_reset_period,
            capabilities=p.capabilities,
            rate_limit_rpm=p.rate_limit_rpm,
            last_verified=p.last_verified.isoformat() if p.last_verified else None,
            is_enabled=p.is_enabled,
            priority=p.priority,
        )
        for p in providers
    ]


@router.get("/providers/{provider_name}/health")
async def provider_health(provider_name: str):
    """Check health of a specific provider"""
    # TODO: Implement actual health checks
    return {
        "provider": provider_name,
        "status": "unknown",
        "message": "Health check not yet implemented",
    }