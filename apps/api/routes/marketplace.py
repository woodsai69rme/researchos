"""
Marketplace routes - Marketplace search and listings
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from uuid import UUID
from decimal import Decimal

from packages.core.database import get_db
from packages.core.logging import get_logger

router = APIRouter()
logger = get_logger("marketplace")


class MarketplaceSearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=500)
    category: Optional[str] = None
    location: Optional[str] = None
    max_price: Optional[float] = Field(None, ge=0)
    min_price: Optional[float] = Field(None, ge=0)
    condition: Optional[List[str]] = None
    seller_type: Optional[List[str]] = None
    sources: Optional[List[str]] = None
    limit: int = Field(default=50, ge=1, le=200)


class ListingResponse(BaseModel):
    id: UUID
    product_id: Optional[UUID]
    source: str
    source_url: str
    title: str
    price: Optional[float]
    currency: str
    seller: Optional[str]
    seller_type: Optional[str]
    location: Optional[str]
    distance_km: Optional[float]
    condition: Optional[str]
    description: Optional[str]
    listing_date: Optional[str]
    shipping_info: Optional[str]
    photos: Optional[List[str]]
    confidence: float
    deal_score: Optional[float]
    deal_score_breakdown: Optional[Dict[str, Any]]


class MarketplaceSearchResponse(BaseModel):
    results: List[ListingResponse]
    total_count: int
    sources_searched: List[str]


@router.post("/search", response_model=MarketplaceSearchResponse)
async def search_marketplace(
    request: MarketplaceSearchRequest,
    db: AsyncSession = Depends(get_db),
):
    """Search marketplace listings"""
    # TODO: Implement actual marketplace search with providers
    # For now, return mock response
    
    mock_results = [
        ListingResponse(
            id=UUID("00000000-0000-0000-0000-000000000001"),
            product_id=None,
            source="gumtree",
            source_url="https://gumtree.com.au/example",
            title=f"{request.query} - Great Condition",
            price=100.0,
            currency="AUD",
            seller="Private Seller",
            seller_type="PRIVATE",
            location=request.location or "Brisbane, QLD",
            distance_km=15.5,
            condition="USED",
            description="Well maintained item, barely used.",
            listing_date="2024-01-15T10:00:00Z",
            shipping_info="Pickup only",
            photos=["https://example.com/photo1.jpg"],
            confidence=0.7,
            deal_score=0.8,
            deal_score_breakdown={"price": 0.9, "condition": 0.7, "seller": 0.8},
        )
    ]
    
    return MarketplaceSearchResponse(
        results=mock_results,
        total_count=len(mock_results),
        sources_searched=request.sources or ["gumtree", "ebay", "facebook_marketplace"],
    )


@router.get("/listings/{listing_id}", response_model=ListingResponse)
async def get_listing(listing_id: UUID, db: AsyncSession = Depends(get_db)):
    """Get listing by ID"""
    from sqlalchemy import select
    from packages.core.models import Listing
    
    result = await db.execute(select(Listing).where(Listing.id == listing_id))
    listing = result.scalar_one_or_none()
    
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    
    return ListingResponse(
        id=listing.id,
        product_id=listing.product_id,
        source=listing.source,
        source_url=listing.source_url,
        title=listing.title,
        price=float(listing.price) if listing.price else None,
        currency=listing.currency,
        seller=listing.seller,
        seller_type=listing.seller_type.value if listing.seller_type else None,
        location=listing.location,
        distance_km=listing.distance_km,
        condition=listing.condition.value if listing.condition else None,
        description=listing.description,
        listing_date=listing.listing_date.isoformat() if listing.listing_date else None,
        shipping_info=listing.shipping_info,
        photos=listing.photos,
        confidence=listing.confidence,
        deal_score=listing.deal_score,
        deal_score_breakdown=listing.deal_score_breakdown,
    )


@router.get("/sources")
async def list_marketplace_sources():
    """List available marketplace sources"""
    return {
        "sources": [
            {"id": "gumtree", "name": "Gumtree", "country": "AU", "requires_auth": False},
            {"id": "ebay", "name": "eBay Australia", "country": "AU", "requires_auth": False},
            {"id": "facebook_marketplace", "name": "Facebook Marketplace", "country": "AU", "requires_auth": True},
            {"id": "carsales", "name": "Carsales", "country": "AU", "requires_auth": False},
            {"id": "carsguide", "name": "CarsGuide", "country": "AU", "requires_auth": False},
            {"id": "pickles", "name": "Pickles Auctions", "country": "AU", "requires_auth": False},
            {"id": "grays", "name": "Grays Online", "country": "AU", "requires_auth": False},
            {"id": "cash_converters", "name": "Cash Converters", "country": "AU", "requires_auth": False},
            {"id": "cex", "name": "CeX", "country": "AU", "requires_auth": False},
        ]
    }