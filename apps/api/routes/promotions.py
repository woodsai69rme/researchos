"""
Promotions routes - Promotion discovery and verification
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime
from decimal import Decimal

from packages.core.database import get_db
from packages.core.logging import get_logger

router = APIRouter()
logger = get_logger("promotions")


class PromotionFilter(BaseModel):
    provider: Optional[str] = None
    status: Optional[str] = None
    country: Optional[str] = None
    active_only: bool = True
    free_only: bool = False


class PromotionResponse(BaseModel):
    id: UUID
    provider: str
    plan: Optional[str]
    offer: str
    amount: Optional[float]
    currency: str
    country: str
    free_limit: Optional[str]
    start_date: Optional[str]
    expiry_date: Optional[str]
    card_required: bool
    auto_renew: bool
    commercial_use: bool
    restrictions: Optional[List[str]]
    official_source_url: Optional[str]
    community_sources: Optional[List[str]]
    last_verified: Optional[str]
    confidence: float
    status: str


class PromotionSearchResponse(BaseModel):
    results: List[PromotionResponse]
    total_count: int


@router.get("/", response_model=PromotionSearchResponse)
async def list_promotions(
    provider: Optional[str] = None,
    status: Optional[str] = None,
    country: str = "AU",
    active_only: bool = True,
    free_only: bool = False,
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
):
    """List promotions with filters"""
    from sqlalchemy import select
    from packages.core.models import Promotion, PromotionStatus
    
    query = select(Promotion)
    
    if provider:
        query = query.where(Promotion.provider == provider)
    if status:
        try:
            st = PromotionStatus(status.upper())
            query = query.where(Promotion.status == st)
        except ValueError:
            pass
    if country:
        query = query.where(Promotion.country == country.upper())
    if active_only:
        query = query.where(Promotion.expiry_date >= datetime.now())
    if free_only:
        query = query.where(Promotion.amount == 0)
    
    query = query.order_by(Promotion.confidence.desc()).limit(limit).offset(offset)
    
    result = await db.execute(query)
    promotions = result.scalars().all()
    
    # Get total count
    from sqlalchemy import func
    count_query = select(func.count(Promotion.id))
    if provider:
        count_query = count_query.where(Promotion.provider == provider)
    if country:
        count_query = count_query.where(Promotion.country == country.upper())
    if active_only:
        count_query = count_query.where(Promotion.expiry_date >= datetime.now())
    if free_only:
        count_query = count_query.where(Promotion.amount == 0)
    
    count_result = await db.execute(count_query)
    total = count_result.scalar() or 0
    
    return PromotionSearchResponse(
        results=[
            PromotionResponse(
                id=p.id,
                provider=p.provider,
                plan=p.plan,
                offer=p.offer,
                amount=float(p.amount) if p.amount else None,
                currency=p.currency,
                country=p.country,
                free_limit=p.free_limit,
                start_date=p.start_date.isoformat() if p.start_date else None,
                expiry_date=p.expiry_date.isoformat() if p.expiry_date else None,
                card_required=p.card_required,
                auto_renew=p.auto_renew,
                commercial_use=p.commercial_use,
                restrictions=p.restrictions,
                official_source_url=p.official_source_url,
                community_sources=p.community_sources,
                last_verified=p.last_verified.isoformat() if p.last_verified else None,
                confidence=p.confidence,
                status=p.status.value,
            )
            for p in promotions
        ],
        total_count=total,
    )


@router.get("/{promotion_id}", response_model=PromotionResponse)
async def get_promotion(promotion_id: UUID, db: AsyncSession = Depends(get_db)):
    """Get promotion by ID"""
    from sqlalchemy import select
    from packages.core.models import Promotion
    
    result = await db.execute(select(Promotion).where(Promotion.id == promotion_id))
    promotion = result.scalar_one_or_none()
    
    if not promotion:
        raise HTTPException(status_code=404, detail="Promotion not found")
    
    return PromotionResponse(
        id=promotion.id,
        provider=promotion.provider,
        plan=promotion.plan,
        offer=promotion.offer,
        amount=float(promotion.amount) if promotion.amount else None,
        currency=promotion.currency,
        country=promotion.country,
        free_limit=promotion.free_limit,
        start_date=promotion.start_date.isoformat() if promotion.start_date else None,
        expiry_date=promotion.expiry_date.isoformat() if promotion.expiry_date else None,
        card_required=promotion.card_required,
        auto_renew=promotion.auto_renew,
        commercial_use=promotion.commercial_use,
        restrictions=promotion.restrictions,
        official_source_url=promotion.official_source_url,
        community_sources=promotion.community_sources,
        last_verified=promotion.last_verified.isoformat() if promotion.last_verified else None,
        confidence=promotion.confidence,
        status=promotion.status.value,
    )


@router.get("/providers/list")
async def list_promotion_providers(db: AsyncSession = Depends(get_db)):
    """List all providers with promotions"""
    from sqlalchemy import select, distinct
    from packages.core.models import Promotion
    
    result = await db.execute(select(distinct(Promotion.provider)))
    providers = result.scalars().all()
    
    return {"providers": sorted(providers)}