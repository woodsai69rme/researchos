"""
Reports routes - Research report generation and retrieval
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from uuid import UUID

from packages.core.database import get_db
from packages.core.logging import get_logger

router = APIRouter()
logger = get_logger("reports")


class ReportResponse(BaseModel):
    id: UUID
    run_id: UUID
    executive_answer: Optional[str]
    bottom_line: Optional[str]
    best_options: Optional[List[Dict[str, Any]]]
    free_options: Optional[List[Dict[str, Any]]]
    cheap_options: Optional[List[Dict[str, Any]]]
    best_value: Optional[List[Dict[str, Any]]]
    similar_options: Optional[List[Dict[str, Any]]]
    alternatives: Optional[List[Dict[str, Any]]]
    marketplace_results: Optional[List[Dict[str, Any]]]
    businesses: Optional[List[Dict[str, Any]]]
    reviews: Optional[List[Dict[str, Any]]]
    community_feedback: Optional[Dict[str, Any]]
    promotions: Optional[List[Dict[str, Any]]]
    pricing: Optional[Dict[str, Any]]
    evidence: Optional[List[Dict[str, Any]]]
    contradictions: Optional[List[Dict[str, Any]]]
    risks: Optional[List[str]]
    unknown_information: Optional[List[str]]
    confidence: float
    last_verified: Optional[str]
    next_check: Optional[str]
    free_only_report: Optional[Dict[str, Any]]
    created_at: str


@router.get("/{run_id}", response_model=ReportResponse)
async def get_report(run_id: UUID, db: AsyncSession = Depends(get_db)):
    """Get report for a research run"""
    from sqlalchemy import select
    from packages.core.models import Report, ResearchRun
    
    # Check if run exists
    run_result = await db.execute(select(ResearchRun).where(ResearchRun.id == run_id))
    run = run_result.scalar_one_or_none()
    
    if not run:
        raise HTTPException(status_code=404, detail="Research run not found")
    
    # Get report
    result = await db.execute(select(Report).where(Report.run_id == run_id))
    report = result.scalar_one_or_none()
    
    if not report:
        raise HTTPException(status_code=404, detail="Report not yet generated")
    
    return ReportResponse(
        id=report.id,
        run_id=report.run_id,
        executive_answer=report.executive_answer,
        bottom_line=report.bottom_line,
        best_options=report.best_options,
        free_options=report.free_options,
        cheap_options=report.cheap_options,
        best_value=report.best_value,
        similar_options=report.similar_options,
        alternatives=report.alternatives,
        marketplace_results=report.marketplace_results,
        businesses=report.businesses,
        reviews=report.reviews,
        community_feedback=report.community_feedback,
        promotions=report.promotions,
        pricing=report.pricing,
        evidence=report.evidence,
        contradictions=report.contradictions,
        risks=report.risks,
        unknown_information=report.unknown_information,
        confidence=report.confidence,
        last_verified=report.last_verified.isoformat() if report.last_verified else None,
        next_check=report.next_check.isoformat() if report.next_check else None,
        free_only_report=report.free_only_report,
        created_at=report.created_at.isoformat(),
    )


@router.post("/{run_id}/generate")
async def generate_report(run_id: UUID, db: AsyncSession = Depends(get_db)):
    """Generate report for a research run"""
    from sqlalchemy import select
    from packages.core.models import Report, ResearchRun, ResearchStatus
    
    result = await db.execute(select(ResearchRun).where(ResearchRun.id == run_id))
    run = result.scalar_one_or_none()
    
    if not run:
        raise HTTPException(status_code=404, detail="Research run not found")
    
    if run.status != ResearchStatus.COMPLETED:
        raise HTTPException(status_code=400, detail=f"Research not completed (status: {run.status})")
    
    # Check if report already exists
    result = await db.execute(select(Report).where(Report.run_id == run_id))
    existing = result.scalar_one_or_none()
    
    if existing:
        return {"success": True, "message": "Report already exists", "report_id": str(existing.id)}
    
    # TODO: Implement actual report generation
    # For now, create a placeholder report
    report = Report(
        run_id=run.id,
        executive_answer="Report generation not yet implemented",
        bottom_line="This is a placeholder report",
        confidence=0.5,
    )
    
    db.add(report)
    await db.commit()
    await db.refresh(report)
    
    return {"success": True, "message": "Report generated", "report_id": str(report.id)}


@router.get("/{run_id}/free-only")
async def get_free_only_report(run_id: UUID, db: AsyncSession = Depends(get_db)):
    """Get free-only mode report"""
    from sqlalchemy import select
    from packages.core.models import Report, ResearchRun
    
    result = await db.execute(select(ResearchRun).where(ResearchRun.id == run_id))
    run = result.scalar_one_or_none()
    
    if not run:
        raise HTTPException(status_code=404, detail="Research run not found")
    
    result = await db.execute(select(Report).where(Report.run_id == run_id))
    report = result.scalar_one_or_none()
    
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    if not report.free_only_report:
        return {
            "run_id": str(run_id),
            "message": "No free-only report available",
            "actual_spend": "0.00",
            "paid_providers_executed": 0,
            "free_providers_used": [],
            "local_models_used": [],
            "free_quotas_consumed": {},
            "remaining_quota": {},
        }
    
    return report.free_only_report