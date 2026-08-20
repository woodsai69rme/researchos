"""
Reviews routes - Review search and sentiment analysis
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from uuid import UUID

from packages.core.database import get_db
from packages.core.logging import get_logger

router = APIRouter()
logger = get_logger("reviews")


class ReviewFilter(BaseModel):
    entity_id: Optional[UUID] = None
    source: Optional[str] = None
    sentiment: Optional[str] = None
    min_rating: Optional[float] = None
    max_rating: Optional[float] = None


class ReviewResponse(BaseModel):
    id: UUID
    entity_id: Optional[UUID]
    source: str
    source_url: Optional[str]
    title: Optional[str]
    text: Optional[str]
    sentiment: str
    rating: Optional[float]
    categories: Optional[List[str]]
    pros: Optional[List[str]]
    cons: Optional[List[str]]
    use_cases: Optional[List[str]]
    limitations: Optional[List[str]]
    bugs_reported: Optional[List[str]]
    author: Optional[str]
    review_date: Optional[str]
    confidence: float


class ReviewSearchResponse(BaseModel):
    results: List[ReviewResponse]
    total_count: int
    sentiment_summary: Dict[str, int]


@router.get("/", response_model=ReviewSearchResponse)
async def list_reviews(
    entity_id: Optional[UUID] = None,
    source: Optional[str] = None,
    sentiment: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
):
    """List reviews with filters"""
    from sqlalchemy import select, func
    from packages.core.models import Review, ReviewSentiment
    
    query = select(Review)
    
    if entity_id:
        query = query.where(Review.entity_id == entity_id)
    if source:
        query = query.where(Review.source == source)
    if sentiment:
        try:
            sent = ReviewSentiment(sentiment.upper())
            query = query.where(Review.sentiment == sent)
        except ValueError:
            pass
    
    query = query.order_by(Review.review_date.desc().nullslast()).limit(limit).offset(offset)
    
    result = await db.execute(query)
    reviews = result.scalars().all()
    
    # Get total count
    count_query = select(func.count(Review.id))
    if entity_id:
        count_query = count_query.where(Review.entity_id == entity_id)
    if source:
        count_query = count_query.where(Review.source == source)
    if sentiment:
        try:
            sent = ReviewSentiment(sentiment.upper())
            count_query = count_query.where(Review.sentiment == sent)
        except ValueError:
            pass
    
    count_result = await db.execute(count_query)
    total = count_result.scalar() or 0
    
    # Sentiment summary
    sentiment_query = select(Review.sentiment, func.count(Review.id)).group_by(Review.sentiment)
    if entity_id:
        sentiment_query = sentiment_query.where(Review.entity_id == entity_id)
    sentiment_result = await db.execute(sentiment_query)
    sentiment_summary = {s.value: c for s, c in sentiment_result.all()}
    
    return ReviewSearchResponse(
        results=[
            ReviewResponse(
                id=r.id,
                entity_id=r.entity_id,
                source=r.source,
                source_url=r.source_url,
                title=r.title,
                text=r.text,
                sentiment=r.sentiment.value,
                rating=r.rating,
                categories=r.categories,
                pros=r.pros,
                cons=r.cons,
                use_cases=r.use_cases,
                limitations=r.limitations,
                bugs_reported=r.bugs_reported,
                author=r.author,
                review_date=r.review_date.isoformat() if r.review_date else None,
                confidence=r.confidence,
            )
            for r in reviews
        ],
        total_count=total,
        sentiment_summary=sentiment_summary,
    )


@router.get("/{review_id}", response_model=ReviewResponse)
async def get_review(review_id: UUID, db: AsyncSession = Depends(get_db)):
    """Get review by ID"""
    from sqlalchemy import select
    from packages.core.models import Review
    
    result = await db.execute(select(Review).where(Review.id == review_id))
    review = result.scalar_one_or_none()
    
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    
    return ReviewResponse(
        id=review.id,
        entity_id=review.entity_id,
        source=review.source,
        source_url=review.source_url,
        title=review.title,
        text=review.text,
        sentiment=review.sentiment.value,
        rating=review.rating,
        categories=review.categories,
        pros=review.pros,
        cons=review.cons,
        use_cases=review.use_cases,
        limitations=review.limitations,
        bugs_reported=review.bugs_reported,
        author=review.author,
        review_date=review.review_date.isoformat() if review.review_date else None,
        confidence=review.confidence,
    )


@router.get("/sentiment/{entity_id}")
async def get_entity_sentiment(entity_id: UUID, db: AsyncSession = Depends(get_db)):
    """Get sentiment analysis for an entity"""
    from sqlalchemy import select, func
    from packages.core.models import Review, ReviewSentiment
    
    # Get sentiment counts
    sentiment_query = select(Review.sentiment, func.count(Review.id)).where(
        Review.entity_id == entity_id
    ).group_by(Review.sentiment)
    
    result = await db.execute(sentiment_query)
    sentiments = {s.value: c for s, c in result.all()}
    
    total = sum(sentiments.values())
    
    # Get recent reviews for analysis
    recent_query = select(Review).where(
        Review.entity_id == entity_id
    ).order_by(Review.review_date.desc().nullslast()).limit(20)
    
    recent_result = await db.execute(recent_query)
    recent = recent_result.scalars().all()
    
    # Extract common themes
    all_pros = []
    all_cons = []
    all_bugs = []
    all_limitations = []
    
    for r in recent:
        if r.pros:
            all_pros.extend(r.pros)
        if r.cons:
            all_cons.extend(r.cons)
        if r.bugs_reported:
            all_bugs.extend(r.bugs_reported)
        if r.limitations:
            all_limitations.extend(r.limitations)
    
    # Count frequencies
    from collections import Counter
    pros_count = Counter(all_pros).most_common(10)
    cons_count = Counter(all_cons).most_common(10)
    bugs_count = Counter(all_bugs).most_common(10)
    limitations_count = Counter(all_limitations).most_common(10)
    
    return {
        "entity_id": str(entity_id),
        "total_reviews": total,
        "sentiment_distribution": sentiments,
        "sentiment_percentages": {
            k: round(v / total * 100, 1) if total > 0 else 0
            for k, v in sentiments.items()
        },
        "top_praise": [{"theme": k, "count": v} for k, v in pros_count],
        "top_complaints": [{"theme": k, "count": v} for k, v in cons_count],
        "top_bugs": [{"theme": k, "count": v} for k, v in bugs_count],
        "top_limitations": [{"theme": k, "count": v} for k, v in limitations_count],
        "community_confidence": min(0.9, total / 100) if total > 0 else 0,
    }