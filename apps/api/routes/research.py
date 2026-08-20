"""
Research routes - Core research functionality
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime

from packages.core.database import get_db
from packages.core.config import settings
from packages.core.logging import get_logger, audit_logger
from packages.core.security import free_policy_engine, FreePolicyMode
from packages.core.models import ResearchRun, ResearchPlan, ResearchStatus, ResearchDepth

router = APIRouter()
logger = get_logger("research")


# ============================================================
# REQUEST/RESPONSE MODELS
# ============================================================

class ResearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=5000, description="Natural language research query")
    project_id: Optional[UUID] = Field(None, description="Project ID to associate with research")
    free_only: Optional[bool] = Field(None, description="Override free-only mode for this run")
    budget_aud: Optional[float] = Field(None, ge=0, le=10000, description="Budget in AUD for this run")
    currency: str = Field(default="AUD", pattern="^[A-Z]{3}$")
    country: str = Field(default="AU", pattern="^[A-Z]{2}$")
    location: Optional[str] = Field(None, max_length=255, description="Specific location (city, region)")
    research_depth: ResearchDepth = Field(default=ResearchDepth.NORMAL)
    monitoring_interval_hours: Optional[int] = Field(None, ge=1, le=168, description="Monitoring interval in hours")
    source_classes: Optional[List[str]] = Field(None, description="Specific source classes to search")
    exclusions: Optional[List[str]] = Field(None, description="Terms to exclude from search")


class ResearchPlanRequest(BaseModel):
    search_queries: List[str] = Field(..., min_length=1)
    required_evidence: Optional[List[str]] = None
    exclusions: Optional[List[str]] = None
    priority: int = 0
    urgency: int = 0
    stop_conditions: Optional[Dict[str, Any]] = None
    estimated_cost_aud: float = 0


class ResearchResponse(BaseModel):
    run_id: UUID
    status: ResearchStatus
    message: str


class ResearchStatusResponse(BaseModel):
    run_id: UUID
    query: str
    normalized_query: Optional[str]
    status: ResearchStatus
    progress: Optional[str]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    total_cost_aud: float
    providers_used: Optional[List[str]]
    error_message: Optional[str]


class ResearchPlanResponse(BaseModel):
    run_id: UUID
    search_queries: List[str]
    required_evidence: Optional[List[str]]
    exclusions: Optional[List[str]]
    priority: int
    urgency: int
    stop_conditions: Optional[Dict[str, Any]]
    estimated_cost_aud: float


# ============================================================
# RESEARCH ENDPOINTS
# ============================================================

@router.post("/start", response_model=ResearchResponse)
async def start_research(
    request: ResearchRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    """Start a new research run"""
    
    # Determine free-only mode
    free_only = request.free_only if request.free_only is not None else settings.FREE_ONLY
    
    # Check budget against policy
    budget = request.budget_aud or 0
    if free_only and budget > 0:
        raise HTTPException(status_code=400, detail="Budget must be 0 in FREE_ONLY mode")
    
    # Verify budget with policy engine
    allowed, reason = free_policy_engine.can_execute("research", budget)
    if not allowed:
        raise HTTPException(status_code=403, detail=f"Budget not allowed: {reason}")
    
    # Create research run
    run = ResearchRun(
        project_id=request.project_id,
        query=request.query,
        budget_aud=budget,
        currency=request.currency,
        free_only=free_only,
        research_depth=request.research_depth,
        monitoring_interval_hours=request.monitoring_interval_hours,
        status=ResearchStatus.PLANNING,
    )
    
    db.add(run)
    await db.commit()
    await db.refresh(run)
    
    # Log audit
    audit_logger.research_started(str(run.id), "anonymous", request.query, free_only)
    
    # Start research in background
    background_tasks.add_task(run_research_pipeline, run.id, request)
    
    logger.info("Research started", run_id=str(run.id), query=request.query[:100], free_only=free_only)
    
    return ResearchResponse(
        run_id=run.id,
        status=run.status,
        message="Research started. Use GET /research/{run_id} to check status.",
    )


async def run_research_pipeline(run_id: UUID, request: ResearchRequest):
    """Background task to run the research pipeline"""
    # This will be implemented with the full pipeline
    # For now, just update status
    from packages.core.database import get_db_context
    from packages.core.models import ResearchStatus
    
    async with get_db_context() as db:
        from sqlalchemy import select
        result = await db.execute(select(ResearchRun).where(ResearchRun.id == run_id))
        run = result.scalar_one_or_none()
        if run:
            run.status = ResearchStatus.SEARCHING
            run.started_at = datetime.now()
            await db.commit()


@router.get("/{run_id}", response_model=ResearchStatusResponse)
async def get_research_status(run_id: UUID, db: AsyncSession = Depends(get_db)):
    """Get research run status"""
    from sqlalchemy import select
    
    result = await db.execute(select(ResearchRun).where(ResearchRun.id == run_id))
    run = result.scalar_one_or_none()
    
    if not run:
        raise HTTPException(status_code=404, detail="Research run not found")
    
    return ResearchStatusResponse(
        run_id=run.id,
        query=run.query,
        normalized_query=run.normalized_query,
        status=run.status,
        progress=None,  # TODO: Add progress tracking
        started_at=run.started_at,
        completed_at=run.completed_at,
        total_cost_aud=float(run.total_cost_aud),
        providers_used=run.providers_used,
        error_message=run.error_message,
    )


@router.get("/{run_id}/plan", response_model=ResearchPlanResponse)
async def get_research_plan(run_id: UUID, db: AsyncSession = Depends(get_db)):
    """Get research plan"""
    from sqlalchemy import select
    
    result = await db.execute(select(ResearchRun).where(ResearchRun.id == run_id))
    run = result.scalar_one_or_none()
    
    if not run:
        raise HTTPException(status_code=404, detail="Research run not found")
    
    if not run.plan:
        raise HTTPException(status_code=404, detail="Research plan not yet generated")
    
    plan = run.plan
    return ResearchPlanResponse(
        run_id=run.id,
        search_queries=plan.search_queries,
        required_evidence=plan.required_evidence,
        exclusions=plan.exclusions,
        priority=plan.priority,
        urgency=plan.urgency,
        stop_conditions=plan.stop_conditions,
        estimated_cost_aud=float(plan.estimated_cost_aud),
    )


@router.post("/{run_id}/plan", response_model=ResearchPlanResponse)
async def create_research_plan(run_id: UUID, request: ResearchPlanRequest, db: AsyncSession = Depends(get_db)):
    """Create or update research plan"""
    from sqlalchemy import select
    
    result = await db.execute(select(ResearchRun).where(ResearchRun.id == run_id))
    run = result.scalar_one_or_none()
    
    if not run:
        raise HTTPException(status_code=404, detail="Research run not found")
    
    if run.plan:
        # Update existing plan
        plan = run.plan
        plan.search_queries = request.search_queries
        plan.required_evidence = request.required_evidence
        plan.exclusions = request.exclusions
        plan.priority = request.priority
        plan.urgency = request.urgency
        plan.stop_conditions = request.stop_conditions
        plan.estimated_cost_aud = request.estimated_cost_aud
    else:
        # Create new plan
        from packages.core.models import ResearchPlan
        plan = ResearchPlan(
            run_id=run.id,
            search_queries=request.search_queries,
            required_evidence=request.required_evidence,
            exclusions=request.exclusions,
            priority=request.priority,
            urgency=request.urgency,
            stop_conditions=request.stop_conditions,
            estimated_cost_aud=request.estimated_cost_aud,
        )
        db.add(plan)
    
    await db.commit()
    await db.refresh(plan)
    
    return ResearchPlanResponse(
        run_id=run.id,
        search_queries=plan.search_queries,
        required_evidence=plan.required_evidence,
        exclusions=plan.exclusions,
        priority=plan.priority,
        urgency=plan.urgency,
        stop_conditions=plan.stop_conditions,
        estimated_cost_aud=float(plan.estimated_cost_aud),
    )


@router.post("/{run_id}/cancel")
async def cancel_research(run_id: UUID, db: AsyncSession = Depends(get_db)):
    """Cancel a research run"""
    from sqlalchemy import select
    from packages.core.models import ResearchStatus
    
    result = await db.execute(select(ResearchRun).where(ResearchRun.id == run_id))
    run = result.scalar_one_or_none()
    
    if not run:
        raise HTTPException(status_code=404, detail="Research run not found")
    
    if run.status in [ResearchStatus.COMPLETED, ResearchStatus.FAILED, ResearchStatus.CANCELLED]:
        raise HTTPException(status_code=400, detail=f"Cannot cancel run in status: {run.status}")
    
    run.status = ResearchStatus.CANCELLED
    run.completed_at = datetime.now()
    await db.commit()
    
    logger.info("Research cancelled", run_id=str(run_id))
    
    return {"success": True, "message": "Research cancelled"}


@router.get("/", response_model=List[ResearchStatusResponse])
async def list_research_runs(
    project_id: Optional[UUID] = None,
    status: Optional[ResearchStatus] = None,
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
):
    """List research runs"""
    from sqlalchemy import select, desc
    
    query = select(ResearchRun).order_by(desc(ResearchRun.created_at))
    
    if project_id:
        query = query.where(ResearchRun.project_id == project_id)
    if status:
        query = query.where(ResearchRun.status == status)
    
    query = query.limit(limit).offset(offset)
    
    result = await db.execute(query)
    runs = result.scalars().all()
    
    return [
        ResearchStatusResponse(
            run_id=run.id,
            query=run.query,
            normalized_query=run.normalized_query,
            status=run.status,
            progress=None,
            started_at=run.started_at,
            completed_at=run.completed_at,
            total_cost_aud=float(run.total_cost_aud),
            providers_used=run.providers_used,
            error_message=run.error_message,
        )
        for run in runs
    ]