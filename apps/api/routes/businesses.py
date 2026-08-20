"""
Businesses routes - Business search and directory
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from uuid import UUID

from packages.core.database import get_db
from packages.core.logging import get_logger

router = APIRouter()
logger = get_logger("businesses")


class BusinessSearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=500)
    category: Optional[str] = None
    location: Optional[str] = None
    radius_km: Optional[float] = Field(default=50, ge=1, le=500)
    services: Optional[List[str]] = None
    specializations: Optional[List[str]] = None
    limit: int = Field(default=50, ge=1, le=200)


class BusinessResponse(BaseModel):
    id: UUID
    name: str
    address: Optional[str]
    suburb: Optional[str]
    state: Optional[str]
    postcode: Optional[str]
    phone: Optional[str]
    website: Optional[str]
    email: Optional[str]
    services: Optional[List[str]]
    specializations: Optional[List[str]]
    business_type: Optional[str]
    confidence: float
    is_verified: bool
    distance_km: Optional[float]


class BusinessSearchResponse(BaseModel):
    results: List[BusinessResponse]
    total_count: int


@router.post("/search", response_model=BusinessSearchResponse)
async def search_businesses(
    request: BusinessSearchRequest,
    db: AsyncSession = Depends(get_db),
):
    """Search for businesses"""
    # TODO: Implement actual business search
    mock_results = [
        BusinessResponse(
            id=UUID("00000000-0000-0000-0000-000000000001"),
            name=f"{request.query} Specialist Workshop",
            address="123 Main Street",
            suburb=request.location or "Brisbane",
            state="QLD",
            postcode="4000",
            phone="07 1234 5678",
            website="https://example.com",
            email="info@example.com",
            services=["Transmission Rebuild", "Performance Tuning"],
            specializations=["TH400", "Ford Barra"],
            business_type="transmission_workshop",
            confidence=0.8,
            is_verified=True,
            distance_km=12.3,
        )
    ]
    
    return BusinessSearchResponse(results=mock_results, total_count=len(mock_results))


@router.get("/{business_id}", response_model=BusinessResponse)
async def get_business(business_id: UUID, db: AsyncSession = Depends(get_db)):
    """Get business by ID"""
    from sqlalchemy import select
    from packages.core.models import Business
    
    result = await db.execute(select(Business).where(Business.id == business_id))
    business = result.scalar_one_or_none()
    
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
    
    return BusinessResponse(
        id=business.id,
        name=business.name,
        address=business.address,
        suburb=business.suburb,
        state=business.state,
        postcode=business.postcode,
        phone=business.phone,
        website=business.website,
        email=business.email,
        services=business.services,
        specializations=business.specializations,
        business_type=business.business_type,
        confidence=business.confidence,
        is_verified=business.is_verified,
        distance_km=None,
    )


@router.get("/{business_id}/reviews")
async def get_business_reviews(business_id: UUID, db: AsyncSession = Depends(get_db)):
    """Get reviews for a business"""
    from sqlalchemy import select
    from packages.core.models import Business, BusinessReview
    
    result = await db.execute(select(Business).where(Business.id == business_id))
    business = result.scalar_one_or_none()
    
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
    
    result = await db.execute(
        select(BusinessReview).where(BusinessReview.business_id == business_id)
    )
    reviews = result.scalars().all()
    
    return {
        "business": business.name,
        "reviews": [
            {
                "source": r.source,
                "rating": r.rating,
                "sentiment": r.sentiment.value,
                "text": r.text,
                "author": r.author,
                "date": r.review_date.isoformat() if r.review_date else None,
            }
            for r in reviews
        ],
    }