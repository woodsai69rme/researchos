"""
ResearchOS Event Bus & Real-Time Event Stream Support
"""
import asyncio
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional
from pydantic import BaseModel, Field


class ResearchEventType(str, Enum):
    RESEARCH_STARTED = "research_started"
    PLANNING_STARTED = "planning_started"
    PLAN_READY = "plan_ready"
    PROVIDER_QUERYING = "provider_querying"
    PROVIDER_SUCCESS = "provider_success"
    PROVIDER_FAILED = "provider_failed"
    PROVIDER_BLOCKED = "provider_blocked"
    SOURCES_DISCOVERED = "sources_discovered"
    DEDUPLICATION_DONE = "deduplication_done"
    EVIDENCE_EXTRACTED = "evidence_extracted"
    CLAIM_EVALUATED = "claim_evaluated"
    CONTRADICTION_FOUND = "contradiction_found"
    MARKETPLACE_SEARCHED = "marketplace_searched"
    BUSINESSES_FOUND = "businesses_found"
    REVIEWS_ANALYZED = "reviews_analyzed"
    MISSING_DISCOVERED = "missing_discovered"
    SYNTHESIS_STARTED = "synthesis_started"
    REPORT_GENERATED = "report_generated"
    RESEARCH_COMPLETED = "research_completed"
    MONITOR_CHECK_STARTED = "monitor_check_started"
    ALERT_TRIGGERED = "alert_triggered"


class ResearchEvent(BaseModel):
    event_id: str = Field(default_factory=lambda: datetime.utcnow().strftime("%Y%m%d%H%M%S%f"))
    run_id: str
    event_type: ResearchEventType
    step_title: str
    message: str
    payload: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class EventBus:
    def __init__(self):
        self._subscribers: Dict[str, List[asyncio.Queue]] = {}
        self._global_listeners: List[Callable[[ResearchEvent], None]] = []

    def subscribe(self, run_id: str) -> asyncio.Queue:
        if run_id not in self._subscribers:
            self._subscribers[run_id] = []
        queue = asyncio.Queue()
        self._subscribers[run_id].append(queue)
        return queue

    def unsubscribe(self, run_id: str, queue: asyncio.Queue):
        if run_id in self._subscribers and queue in self._subscribers[run_id]:
            self._subscribers[run_id].remove(queue)
            if not self._subscribers[run_id]:
                del self._subscribers[run_id]

    async def emit(self, event: ResearchEvent):
        # Dispatch to specific run subscribers
        if event.run_id in self._subscribers:
            for q in self._subscribers[event.run_id]:
                await q.put(event)
        
        # Dispatch to global listeners
        for listener in self._global_listeners:
            try:
                listener(event)
            except Exception:
                pass


event_bus = EventBus()
