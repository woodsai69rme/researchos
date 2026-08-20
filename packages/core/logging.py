"""
ResearchOS Logging Module
Structured logging with structlog and JSON output
"""
import sys
import logging
import structlog
from typing import Any, Dict
from pythonjsonlogger import jsonlogger

from .config import settings


def setup_logging() -> None:
    """Configure structured logging for ResearchOS"""

    # Standard library logging config
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, settings.LOG_LEVEL),
    )

    # Configure structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso", utc=True),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer()
            if settings.ENVIRONMENT == "production"
            else structlog.dev.ConsoleRenderer(colors=True),
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    # Set specific logger levels
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """Get a structured logger instance"""
    return structlog.get_logger(name)


class AuditLogger:
    """Specialized logger for audit events"""

    def __init__(self):
        self.logger = get_logger("audit")

    def log(
        self,
        event_type: str,
        user_id: str = None,
        run_id: str = None,
        provider: str = None,
        details: Dict[str, Any] = None,
        ip_address: str = None,
        user_agent: str = None,
    ) -> None:
        """Log an audit event"""
        self.logger.info(
            "audit_event",
            event_type=event_type,
            user_id=user_id,
            run_id=run_id,
            provider=provider,
            details=details or {},
            ip_address=ip_address,
            user_agent=user_agent,
        )

    def research_started(self, run_id: str, user_id: str, query: str, free_only: bool) -> None:
        self.log("research_started", run_id=run_id, user_id=user_id, details={"query": query, "free_only": free_only})

    def provider_selected(self, run_id: str, provider: str, reason: str) -> None:
        self.log("provider_selected", run_id=run_id, provider=provider, details={"reason": reason})

    def provider_rejected(self, run_id: str, provider: str, reason: str) -> None:
        self.log("provider_rejected", run_id=run_id, provider=provider, details={"reason": reason})

    def provider_failed(self, run_id: str, provider: str, error: str) -> None:
        self.log("provider_failed", run_id=run_id, provider=provider, details={"error": error})

    def api_call(self, run_id: str, provider: str, operation: str, cost_aud: float = 0) -> None:
        self.log("api_call", run_id=run_id, provider=provider, details={"operation": operation, "cost_aud": cost_aud})

    def quota_exhausted(self, run_id: str, provider: str, quota_type: str) -> None:
        self.log("quota_exhausted", run_id=run_id, provider=provider, details={"quota_type": quota_type})

    def search_completed(self, run_id: str, provider: str, query: str, results_count: int) -> None:
        self.log("search_completed", run_id=run_id, provider=provider, details={"query": query, "results_count": results_count})

    def source_discovered(self, run_id: str, source_url: str, tier: str) -> None:
        self.log("source_discovered", run_id=run_id, details={"source_url": source_url, "tier": tier})

    def claim_created(self, run_id: str, claim_id: str, claim_text: str) -> None:
        self.log("claim_created", run_id=run_id, details={"claim_id": claim_id, "claim_text": claim_text[:200]})

    def claim_verified(self, run_id: str, claim_id: str, status: str) -> None:
        self.log("claim_verified", run_id=run_id, details={"claim_id": claim_id, "status": status})

    def contradiction_found(self, run_id: str, claim_id: str, contradiction_type: str) -> None:
        self.log("contradiction_found", run_id=run_id, details={"claim_id": claim_id, "type": contradiction_type})

    def report_generated(self, run_id: str, report_id: str, confidence: float) -> None:
        self.log("report_generated", run_id=run_id, details={"report_id": report_id, "confidence": confidence})

    def monitor_run(self, watchlist_id: str, changes: int) -> None:
        self.log("monitor_run", details={"watchlist_id": watchlist_id, "changes_detected": changes})

import re

SECRET_PATTERNS = [
    re.compile(r"(sk-or-v1-[a-zA-Z0-9]{32,})"),
    re.compile(r"(AIzaSy[a-zA-Z0-9_-]{33})"),
    re.compile(r"(ghp_[a-zA-Z0-9]{36,})"),
    re.compile(r"(Bearer\s+[a-zA-Z0-9_\-\.]{16,})", re.IGNORECASE),
]


def redact_secrets(text: str) -> str:
    if not isinstance(text, str):
        return str(text)
    redacted = text
    for pattern in SECRET_PATTERNS:
        redacted = pattern.sub(r"[REDACTED_SECRET]", redacted)
    return redacted


def setup_logger(name: str = "ResearchOS"):
    return logging.getLogger(name)


# Global audit logger instance
audit_logger = AuditLogger()
logger = logging.getLogger("ResearchOS")