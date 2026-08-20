"""
ResearchOS Master FastAPI Backend Server
"""
import asyncio
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from fastapi import FastAPI, BackgroundTasks, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from researchos.packages.core.config import settings, OperatingMode, ResearchDepth
from researchos.packages.core.logging import logger
from researchos.packages.core.schemas import (
    ResearchPlan, FinalResearchReport, Watchlist, Alert, Promotion, ModelSpec, VideoProviderCost
)
from researchos.packages.core.events import event_bus, ResearchEvent, ResearchEventType
from researchos.packages.security.policy import policy_enforcer
from researchos.packages.providers.registry import provider_registry
from researchos.packages.research.planner import ResearchPlanner
from researchos.packages.research.swarm import SearchSwarm
from researchos.packages.research.synthesis import ResearchSynthesizer
from researchos.packages.models.catalog import model_catalog
from researchos.packages.pricing.video_costs import VideoCostEngine
from researchos.packages.promotions.hunter import PromotionHunter
from researchos.packages.business.automotive import automotive_engine
from researchos.packages.monitoring.watchlists import monitoring_engine
from researchos.db.database import init_db, SessionLocal, ResearchRunRecord

# Initialize Database Schema
init_db()

app = FastAPI(
    title="ResearchOS Universal Deep Research API",
    description="Universal AI-powered Search, Deep Research, Deal Hunter, Review Analysis & Continuous Monitoring OS",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

planner = ResearchPlanner()
swarm = SearchSwarm()
synthesizer = ResearchSynthesizer()
video_engine = VideoCostEngine()
promo_hunter = PromotionHunter()

# In-memory cached runs for instant retrieval
run_cache: Dict[str, FinalResearchReport] = {}


class ResearchRequest(BaseModel):
    query: str = Field(..., description="Natural language search/research query")
    mode: OperatingMode = Field(default=OperatingMode.FREE_ONLY)
    depth: ResearchDepth = Field(default=ResearchDepth.NORMAL)
    location: str = Field(default="Brisbane, Queensland, Australia")
    budget: float = Field(default=0.0)
    monitor_interval: Optional[int] = Field(default=None, description="Interval in hours to auto-monitor")


@app.get("/api/health")
async def health_check():
    return {
        "status": "online",
        "app": getattr(settings, "APP_NAME", "ResearchOS"),
        "version": getattr(settings, "APP_VERSION", "1.0.0"),
        "operating_mode": settings.OPERATING_MODE.value if hasattr(settings, "OPERATING_MODE") else "FREE_ONLY",
        "free_only_enforced": getattr(settings, "FREE_ONLY", True),
        "default_currency": getattr(settings, "DEFAULT_CURRENCY", "AUD"),
        "default_location": getattr(settings, "DEFAULT_LOCATION", "Brisbane, Queensland, Australia"),
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.post("/api/research/plan", response_model=ResearchPlan)
async def generate_plan(req: ResearchRequest):
    plan = planner.create_plan(
        user_query=req.query,
        mode=req.mode,
        depth=req.depth,
        location=req.location,
        budget=req.budget,
    )
    return plan


@app.post("/api/research/execute", response_model=FinalResearchReport)
async def execute_research(req: ResearchRequest, background_tasks: BackgroundTasks):
    policy_enforcer.set_mode(req.mode)

    plan = planner.create_plan(
        user_query=req.query,
        mode=req.mode,
        depth=req.depth,
        location=req.location,
        budget=req.budget,
    )
    plan.monitoring_interval = req.monitor_interval

    await event_bus.emit(
        ResearchEvent(
            run_id=plan.plan_id,
            event_type=ResearchEventType.PLAN_READY,
            step_title="Research Plan Generated",
            message=f"Expanded query into {len(plan.search_queries)} search variants across {len(plan.source_classes)} channels.",
            payload={"plan_id": plan.plan_id, "entities": plan.entities},
        )
    )

    swarm_results = await swarm.execute_swarm(plan)
    report = await synthesizer.synthesize(plan, swarm_results)
    run_cache[report.report_id] = report

    try:
        db = SessionLocal()
        record = ResearchRunRecord(
            id=report.report_id,
            query=req.query,
            operating_mode=req.mode.value,
            depth=req.depth.value,
            location=req.location,
            actual_spend_aud=report.actual_spend_aud,
            report_json=report.model_dump(mode="json"),
        )
        db.add(record)
        db.commit()
        db.close()
    except Exception as e:
        logger.warning(f"Error persisting research run: {e}")

    if req.monitor_interval:
        monitoring_engine.add_watchlist(
            title=f"Monitor: {req.query[:40]}",
            query=req.query,
            category=plan.domain_category,
            interval_hours=req.monitor_interval,
        )

    return report


@app.get("/api/research/stream/{run_id}")
async def stream_research_events(run_id: str):
    async def event_generator():
        queue = event_bus.subscribe(run_id)
        try:
            while True:
                try:
                    event: ResearchEvent = await asyncio.wait_for(queue.get(), timeout=20.0)
                    data = json.dumps({
                        "event_type": event.event_type.value,
                        "step_title": event.step_title,
                        "message": event.message,
                        "payload": event.payload,
                        "timestamp": event.timestamp.isoformat(),
                    })
                    yield f"data: {data}\n\n"
                    if event.event_type in (ResearchEventType.REPORT_GENERATED, ResearchEventType.RESEARCH_COMPLETED):
                        break
                except asyncio.TimeoutError:
                    yield f": ping\n\n"
        finally:
            event_bus.unsubscribe(run_id, queue)

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@app.get("/api/research/{report_id}", response_model=FinalResearchReport)
async def get_report(report_id: str):
    if report_id in run_cache:
        return run_cache[report_id]
    
    db = SessionLocal()
    rec = db.query(ResearchRunRecord).filter(ResearchRunRecord.id == report_id).first()
    db.close()
    if rec and rec.report_json:
        return FinalResearchReport(**rec.report_json)
    raise HTTPException(status_code=404, detail="Research report not found")


@app.get("/api/research/{report_id}/export/markdown")
async def export_markdown(report_id: str):
    report = await get_report(report_id)
    from researchos.packages.research.exporter import report_exporter
    from fastapi.responses import PlainTextResponse
    filepath = report_exporter.export_to_markdown(report)
    content = Path(filepath).read_text(encoding="utf-8")
    return PlainTextResponse(content, media_type="text/markdown", headers={"Content-Disposition": f"attachment; filename=Report_{report_id}.md"})


@app.get("/api/research/{report_id}/export/json")
async def export_json(report_id: str):
    report = await get_report(report_id)
    from researchos.packages.research.exporter import report_exporter
    from fastapi.responses import PlainTextResponse
    filepath = report_exporter.export_to_json(report)
    content = Path(filepath).read_text(encoding="utf-8")
    return PlainTextResponse(content, media_type="application/json", headers={"Content-Disposition": f"attachment; filename=Report_{report_id}.json"})


@app.get("/api/research/{report_id}/export/csv")
async def export_csv(report_id: str):
    report = await get_report(report_id)
    from researchos.packages.research.exporter import report_exporter
    from fastapi.responses import PlainTextResponse
    filepath = report_exporter.export_to_csv(report)
    content = Path(filepath).read_text(encoding="utf-8")
    return PlainTextResponse(content, media_type="text/csv", headers={"Content-Disposition": f"attachment; filename=Deals_{report_id}.csv"})


@app.get("/api/models", response_model=List[ModelSpec])
async def list_models(free_only: bool = True):
    return model_catalog.get_models(free_only=free_only)


@app.get("/api/video-costs", response_model=List[VideoProviderCost])
async def list_video_costs(minutes: float = Query(default=3.5, description="Length of music video in minutes")):
    return video_engine.calculate_all_costs(music_video_minutes=minutes)


@app.get("/api/promotions", response_model=List[Promotion])
async def list_promotions(query: str = ""):
    return promo_hunter.discover_promotions(query=query)


@app.get("/api/automotive/spec")
async def get_automotive_specs(query: str = "XR6 Turbo TH400"):
    return automotive_engine.verify_compatibility(query)


@app.get("/api/watchlists", response_model=List[Watchlist])
async def get_watchlists():
    return monitoring_engine.get_all_watchlists()


@app.post("/api/watchlists", response_model=Watchlist)
async def create_watchlist(title: str, query: str, category: str = "general", interval_hours: int = 12):
    return monitoring_engine.add_watchlist(title=title, query=query, category=category, interval_hours=interval_hours)


@app.get("/api/alerts", response_model=List[Alert])
async def get_alerts():
    return monitoring_engine.get_recent_alerts()


@app.get("/api/providers/health")
async def get_provider_health():
    return await provider_registry.get_all_provider_health()


@app.get("/api/history")
async def get_history(limit: int = 10):
    db = SessionLocal()
    runs = db.query(ResearchRunRecord).order_by(ResearchRunRecord.created_at.desc()).limit(limit).all()
    db.close()
    return [
        {
            "id": r.id,
            "query": r.query,
            "operating_mode": r.operating_mode,
            "location": r.location,
            "actual_spend_aud": r.actual_spend_aud,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        }
        for r in runs
    ]


web_dir = Path(__file__).resolve().parent.parent / "web" / "public"
if web_dir.exists():
    app.mount("/static", StaticFiles(directory=str(web_dir)), name="static")

    @app.get("/")
    async def serve_index():
        return FileResponse(str(web_dir / "index.html"))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("researchos.apps.api.main:app", host="0.0.0.0", port=8000, reload=True)