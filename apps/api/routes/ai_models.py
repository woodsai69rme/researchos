"""
AI Models routes - AI model catalogue and comparison
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from uuid import UUID

from packages.core.database import get_db
from packages.core.logging import get_logger

router = APIRouter()
logger = get_logger("ai_models")


class AIModelFilter(BaseModel):
    provider: Optional[str] = None
    has_vision: Optional[bool] = None
    has_audio: Optional[bool] = None
    has_tool_use: Optional[bool] = None
    has_reasoning: Optional[bool] = None
    free_only: Optional[bool] = None
    max_price_per_million: Optional[float] = None
    min_context_window: Optional[int] = None
    modalities: Optional[List[str]] = None


class AIModelResponse(BaseModel):
    id: UUID
    provider: str
    model_id: str
    model_name: str
    version: Optional[str]
    context_window: Optional[int]
    modalities: Optional[List[str]]
    has_vision: bool
    has_audio: bool
    has_tool_use: bool
    has_reasoning: bool
    coding_score: Optional[float]
    agent_capabilities: Optional[List[str]]
    api_availability: bool
    free_availability: bool
    free_limits: Optional[Dict[str, Any]]
    price_per_million_tokens: Optional[float]
    speed_tokens_per_sec: Optional[float]
    last_verified: Optional[str]
    benchmark_scores: Optional[Dict[str, Any]]


class AIModelSearchResponse(BaseModel):
    results: List[AIModelResponse]
    total_count: int
    rankings: Dict[str, List[str]]


@router.get("/", response_model=AIModelSearchResponse)
async def list_ai_models(
    provider: Optional[str] = None,
    free_only: bool = False,
    has_vision: Optional[bool] = None,
    has_tool_use: Optional[bool] = None,
    min_context: Optional[int] = None,
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
):
    """List AI models with filters"""
    from sqlalchemy import select
    from packages.core.models import AIModel
    
    query = select(AIModel)
    
    if provider:
        query = query.where(AIModel.provider == provider)
    if free_only:
        query = query.where(AIModel.free_availability == True)
    if has_vision is not None:
        query = query.where(AIModel.has_vision == has_vision)
    if has_tool_use is not None:
        query = query.where(AIModel.has_tool_use == has_tool_use)
    if min_context:
        query = query.where(AIModel.context_window >= min_context)
    
    query = query.order_by(AIModel.provider, AIModel.model_name).limit(limit).offset(offset)
    
    result = await db.execute(query)
    models = result.scalars().all()
    
    # Get total count
    from sqlalchemy import func
    count_query = select(func.count(AIModel.id))
    if provider:
        count_query = count_query.where(AIModel.provider == provider)
    if free_only:
        count_query = count_query.where(AIModel.free_availability == True)
    if has_vision is not None:
        count_query = count_query.where(AIModel.has_vision == has_vision)
    if has_tool_use is not None:
        count_query = count_query.where(AIModel.has_tool_use == has_tool_use)
    if min_context:
        count_query = count_query.where(AIModel.context_window >= min_context)
    
    count_result = await db.execute(count_query)
    total = count_result.scalar() or 0
    
    # Generate rankings
    rankings = {
        "best_free": [m.model_name for m in models if m.free_availability][:5],
        "best_coding": [m.model_name for m in sorted(models, key=lambda x: x.coding_score or 0, reverse=True)][:5],
        "best_context": [m.model_name for m in sorted(models, key=lambda x: x.context_window or 0, reverse=True)][:5],
        "best_speed": [m.model_name for m in sorted(models, key=lambda x: x.speed_tokens_per_sec or 0, reverse=True)][:5],
    }
    
    return AIModelSearchResponse(
        results=[
            AIModelResponse(
                id=m.id,
                provider=m.provider,
                model_id=m.model_id,
                model_name=m.model_name,
                version=m.version,
                context_window=m.context_window,
                modalities=m.modalities,
                has_vision=m.has_vision,
                has_audio=m.has_audio,
                has_tool_use=m.has_tool_use,
                has_reasoning=m.has_reasoning,
                coding_score=m.coding_score,
                agent_capabilities=m.agent_capabilities,
                api_availability=m.api_availability,
                free_availability=m.free_availability,
                free_limits=m.free_limits,
                price_per_million_tokens=float(m.price_per_million_tokens) if m.price_per_million_tokens else None,
                speed_tokens_per_sec=m.speed_tokens_per_sec,
                last_verified=m.last_verified.isoformat() if m.last_verified else None,
                benchmark_scores=m.benchmark_scores,
            )
            for m in models
        ],
        total_count=total,
        rankings=rankings,
    )


@router.get("/{model_id}", response_model=AIModelResponse)
async def get_ai_model(model_id: UUID, db: AsyncSession = Depends(get_db)):
    """Get AI model by ID"""
    from sqlalchemy import select
    from packages.core.models import AIModel
    
    result = await db.execute(select(AIModel).where(AIModel.id == model_id))
    model = result.scalar_one_or_none()
    
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
    
    return AIModelResponse(
        id=model.id,
        provider=model.provider,
        model_id=model.model_id,
        model_name=model.model_name,
        version=model.version,
        context_window=model.context_window,
        modalities=model.modalities,
        has_vision=model.has_vision,
        has_audio=model.has_audio,
        has_tool_use=model.has_tool_use,
        has_reasoning=model.has_reasoning,
        coding_score=model.coding_score,
        agent_capabilities=model.agent_capabilities,
        api_availability=model.api_availability,
        free_availability=model.free_availability,
        free_limits=model.free_limits,
        price_per_million_tokens=float(model.price_per_million_tokens) if model.price_per_million_tokens else None,
        speed_tokens_per_sec=model.speed_tokens_per_sec,
        last_verified=model.last_verified.isoformat() if model.last_verified else None,
        benchmark_scores=model.benchmark_scores,
    )


@router.get("/providers/list")
async def list_ai_providers(db: AsyncSession = Depends(get_db)):
    """List all AI model providers"""
    from sqlalchemy import select, distinct
    from packages.core.models import AIModel
    
    result = await db.execute(select(distinct(AIModel.provider)))
    providers = result.scalars().all()
    
    return {"providers": sorted(providers)}


@router.get("/rankings/{category}")
async def get_rankings(category: str, db: AsyncSession = Depends(get_db)):
    """Get model rankings by category"""
    from sqlalchemy import select
    from packages.core.models import AIModel
    
    result = await db.execute(select(AIModel))
    models = result.scalars().all()
    
    rankings = {}
    
    if category == "best_free":
        ranked = sorted([m for m in models if m.free_availability], key=lambda x: x.coding_score or 0, reverse=True)
        rankings["best_free"] = [{"name": m.model_name, "provider": m.provider, "coding_score": m.coding_score} for m in ranked[:10]]
    elif category == "best_coding":
        ranked = sorted(models, key=lambda x: x.coding_score or 0, reverse=True)
        rankings["best_coding"] = [{"name": m.model_name, "provider": m.provider, "coding_score": m.coding_score} for m in ranked[:10]]
    elif category == "best_context":
        ranked = sorted(models, key=lambda x: x.context_window or 0, reverse=True)
        rankings["best_context"] = [{"name": m.model_name, "provider": m.provider, "context_window": m.context_window} for m in ranked[:10]]
    elif category == "best_speed":
        ranked = sorted(models, key=lambda x: x.speed_tokens_per_sec or 0, reverse=True)
        rankings["best_speed"] = [{"name": m.model_name, "provider": m.provider, "speed": m.speed_tokens_per_sec} for m in ranked[:10]]
    elif category == "best_value":
        # Free models with good capabilities
        ranked = sorted([m for m in models if m.free_availability], key=lambda x: (x.has_tool_use, x.has_reasoning, x.coding_score or 0), reverse=True)
        rankings["best_value"] = [{"name": m.model_name, "provider": m.provider, "free": m.free_availability} for m in ranked[:10]]
    else:
        raise HTTPException(status_code=400, detail=f"Unknown ranking category: {category}")
    
    return rankings