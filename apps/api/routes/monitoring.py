"""
Monitoring routes - Watchlists and change detection
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime

from packages.core.database import get_db
from packages.core.logging import get_logger

router = APIRouter()
logger = get_logger("monitoring")


class WatchlistCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    watchlist_type: str = Field(..., pattern="^(AI_MODELS|AI_TOOLS|AI_CODING|AI_VIDEO|PRICES|FREE_TIERS|PROMOTIONS|MARKETPLACES|PRODUCTS|BUSINESSES|WORKSHOPS|GITHUB_REPOS|FORUMS|NEWS|COMPANIES)$")
    query: Optional[str] = None
    filters: Optional[Dict[str, Any]] = None
    interval_hours: int = Field(default=24, ge=1, le=168)
    alert_channels: Optional[List[str]] = None
    alert_threshold: Optional[Dict[str, Any]] = None


class WatchlistUpdate(BaseModel):
    name: Optional[str] = None
    query: Optional[str] = None
    filters: Optional[Dict[str, Any]] = None
    interval_hours: Optional[int] = None
    is_active: Optional[bool] = None
    alert_channels: Optional[List[str]] = None
    alert_threshold: Optional[Dict[str, Any]] = None


class WatchlistResponse(BaseModel):
    id: UUID
    name: str
    watchlist_type: str
    query: Optional[str]
    filters: Optional[Dict[str, Any]]
    interval_hours: int
    is_active: bool
    last_run: Optional[str]
    next_run: Optional[str]
    alert_channels: Optional[List[str]]
    alert_threshold: Optional[Dict[str, Any]]
    created_at: str


class WatchlistSearchResponse(BaseModel):
    results: List[WatchlistResponse]
    total_count: int


@router.post("/watchlists", response_model=WatchlistResponse)
async def create_watchlist(
    request: WatchlistCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new watchlist"""
    from packages.core.models import Watchlist, WatchlistType, AlertChannel
    from sqlalchemy import select
    
    try:
        wt = WatchlistType(request.watchlist_type)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid watchlist type: {request.watchlist_type}")
    
    alert_channels = None
    if request.alert_channels:
        try:
            alert_channels = [AlertChannel(c) for c in request.alert_channels]
        except ValueError as e:
            raise HTTPException(status_code=400, detail=f"Invalid alert channel: {e}")
    
    watchlist = Watchlist(
        user_id=UUID("00000000-0000-0000-0000-000000000001"),  # TODO: Get from auth
        name=request.name,
        watchlist_type=wt,
        query=request.query,
        filters=request.filters,
        interval_hours=request.interval_hours,
        alert_channels=alert_channels,
        alert_threshold=request.alert_threshold,
    )
    
    db.add(watchlist)
    await db.commit()
    await db.refresh(watchlist)
    
    return WatchlistResponse(
        id=watchlist.id,
        name=watchlist.name,
        watchlist_type=watchlist.watchlist_type.value,
        query=watchlist.query,
        filters=watchlist.filters,
        interval_hours=watchlist.interval_hours,
        is_active=watchlist.is_active,
        last_run=watchlist.last_run.isoformat() if watchlist.last_run else None,
        next_run=watchlist.next_run.isoformat() if watchlist.next_run else None,
        alert_channels=[c.value for c in watchlist.alert_channels] if watchlist.alert_channels else None,
        alert_threshold=watchlist.alert_threshold,
        created_at=watchlist.created_at.isoformat(),
    )


@router.get("/watchlists", response_model=WatchlistSearchResponse)
async def list_watchlists(
    active_only: bool = True,
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
):
    """List watchlists"""
    from sqlalchemy import select, func
    from packages.core.models import Watchlist
    
    query = select(Watchlist)
    
    if active_only:
        query = query.where(Watchlist.is_active == True)
    
    query = query.order_by(Watchlist.created_at.desc()).limit(limit).offset(offset)
    
    result = await db.execute(query)
    watchlists = result.scalars().all()
    
    count_query = select(func.count(Watchlist.id))
    if active_only:
        count_query = count_query.where(Watchlist.is_active == True)
    count_result = await db.execute(count_query)
    total = count_result.scalar() or 0
    
    return WatchlistSearchResponse(
        results=[
            WatchlistResponse(
                id=w.id,
                name=w.name,
                watchlist_type=w.watchlist_type.value,
                query=w.query,
                filters=w.filters,
                interval_hours=w.interval_hours,
                is_active=w.is_active,
                last_run=w.last_run.isoformat() if w.last_run else None,
                next_run=w.next_run.isoformat() if w.next_run else None,
                alert_channels=[c.value for c in w.alert_channels] if w.alert_channels else None,
                alert_threshold=w.alert_threshold,
                created_at=w.created_at.isoformat(),
            )
            for w in watchlists
        ],
        total_count=total,
    )


@router.get("/watchlists/{watchlist_id}", response_model=WatchlistResponse)
async def get_watchlist(watchlist_id: UUID, db: AsyncSession = Depends(get_db)):
    """Get watchlist by ID"""
    from sqlalchemy import select
    from packages.core.models import Watchlist
    
    result = await db.execute(select(Watchlist).where(Watchlist.id == watchlist_id))
    watchlist = result.scalar_one_or_none()
    
    if not watchlist:
        raise HTTPException(status_code=404, detail="Watchlist not found")
    
    return WatchlistResponse(
        id=watchlist.id,
        name=watchlist.name,
        watchlist_type=watchlist.watchlist_type.value,
        query=watchlist.query,
        filters=watchlist.filters,
        interval_hours=watchlist.interval_hours,
        is_active=watchlist.is_active,
        last_run=watchlist.last_run.isoformat() if watchlist.last_run else None,
        next_run=watchlist.next_run.isoformat() if watchlist.next_run else None,
        alert_channels=[c.value for c in watchlist.alert_channels] if watchlist.alert_channels else None,
        alert_threshold=watchlist.alert_threshold,
        created_at=watchlist.created_at.isoformat(),
    )


@router.patch("/watchlists/{watchlist_id}", response_model=WatchlistResponse)
async def update_watchlist(
    watchlist_id: UUID,
    update: WatchlistUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update a watchlist"""
    from sqlalchemy import select
    from packages.core.models import Watchlist, AlertChannel
    
    result = await db.execute(select(Watchlist).where(Watchlist.id == watchlist_id))
    watchlist = result.scalar_one_or_none()
    
    if not watchlist:
        raise HTTPException(status_code=404, detail="Watchlist not found")
    
    update_data = update.model_dump(exclude_unset=True)
    
    if "alert_channels" in update_data and update_data["alert_channels"]:
        try:
            update_data["alert_channels"] = [AlertChannel(c) for c in update_data["alert_channels"]]
        except ValueError as e:
            raise HTTPException(status_code=400, detail=f"Invalid alert channel: {e}")
    
    for field, value in update_data.items():
        setattr(watchlist, field, value)
    
    await db.commit()
    await db.refresh(watchlist)
    
    return WatchlistResponse(
        id=watchlist.id,
        name=watchlist.name,
        watchlist_type=watchlist.watchlist_type.value,
        query=watchlist.query,
        filters=watchlist.filters,
        interval_hours=watchlist.interval_hours,
        is_active=watchlist.is_active,
        last_run=watchlist.last_run.isoformat() if watchlist.last_run else None,
        next_run=watchlist.next_run.isoformat() if watchlist.next_run else None,
        alert_channels=[c.value for c in watchlist.alert_channels] if watchlist.alert_channels else None,
        alert_threshold=watchlist.alert_threshold,
        created_at=watchlist.created_at.isoformat(),
    )


@router.delete("/watchlists/{watchlist_id}")
async def delete_watchlist(watchlist_id: UUID, db: AsyncSession = Depends(get_db)):
    """Delete a watchlist"""
    from sqlalchemy import select
    from packages.core.models import Watchlist
    
    result = await db.execute(select(Watchlist).where(Watchlist.id == watchlist_id))
    watchlist = result.scalar_one_or_none()
    
    if not watchlist:
        raise HTTPException(status_code=404, detail="Watchlist not found")
    
    await db.delete(watchlist)
    await db.commit()
    
    return {"success": True, "message": "Watchlist deleted"}


@router.post("/watchlists/{watchlist_id}/run")
async def run_watchlist(watchlist_id: UUID, db: AsyncSession = Depends(get_db)):
    """Manually trigger a watchlist run"""
    from sqlalchemy import select
    from packages.core.models import Watchlist
    
    result = await db.execute(select(Watchlist).where(Watchlist.id == watchlist_id))
    watchlist = result.scalar_one_or_none()
    
    if not watchlist:
        raise HTTPException(status_code=404, detail="Watchlist not found")
    
    # TODO: Implement actual watchlist run
    return {
        "watchlist_id": str(watchlist_id),
        "status": "started",
        "message": "Watchlist run initiated (not yet implemented)",
    }


@router.get("/watchlists/{watchlist_id}/runs")
async def get_watchlist_runs(
    watchlist_id: UUID,
    limit: int = 20,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
):
    """Get watchlist run history"""
    from sqlalchemy import select
    from packages.core.models import Watchlist, MonitorRun
    
    result = await db.execute(select(Watchlist).where(Watchlist.id == watchlist_id))
    watchlist = result.scalar_one_or_none()
    
    if not watchlist:
        raise HTTPException(status_code=404, detail="Watchlist not found")
    
    result = await db.execute(
        select(MonitorRun)
        .where(MonitorRun.watchlist_id == watchlist_id)
        .order_by(MonitorRun.started_at.desc())
        .limit(limit)
        .offset(offset)
    )
    runs = result.scalars().all()
    
    return {
        "watchlist_id": str(watchlist_id),
        "runs": [
            {
                "id": str(r.id),
                "status": r.status,
                "started_at": r.started_at.isoformat(),
                "completed_at": r.completed_at.isoformat() if r.completed_at else None,
                "changes_detected": r.changes_detected,
                "new_items": r.new_items,
                "updated_items": r.updated_items,
                "removed_items": r.removed_items,
                "error": r.error,
            }
            for r in runs
        ],
    }


@router.get("/alerts")
async def list_alerts(
    unread_only: bool = False,
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
):
    """List alerts"""
    from sqlalchemy import select, func
    from packages.core.models import Alert
    
    query = select(Alert)
    
    if unread_only:
        query = query.where(Alert.is_read == False)
    
    query = query.order_by(Alert.created_at.desc()).limit(limit).offset(offset)
    
    result = await db.execute(query)
    alerts = result.scalars().all()
    
    count_query = select(func.count(Alert.id))
    if unread_only:
        count_query = count_query.where(Alert.is_read == False)
    count_result = await db.execute(count_query)
    total = count_result.scalar() or 0
    
    return {
        "alerts": [
            {
                "id": str(a.id),
                "channel": a.channel.value,
                "title": a.title,
                "message": a.message,
                "severity": a.severity,
                "is_read": a.is_read,
                "is_sent": a.is_sent,
                "created_at": a.created_at.isoformat(),
                "data": a.data,
            }
            for a in alerts
        ],
        total_count: total,
    }


@router.post("/alerts/{alert_id}/read")
async def mark_alert_read(alert_id: UUID, db: AsyncSession = Depends(get_db)):
    """Mark alert as read"""
    from sqlalchemy import select
    from packages.core.models import Alert
    
    result = await db.execute(select(Alert).where(Alert.id == alert_id))
    alert = result.scalar_one_or_none()
    
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    alert.is_read = True
    await db.commit()
    
    return {"success": True}