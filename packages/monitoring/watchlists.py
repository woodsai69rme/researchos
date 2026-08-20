"""
ResearchOS Continuous Monitoring & Watchlist Engine
"""
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from researchos.packages.core.schemas import Watchlist, Alert
from researchos.packages.core.logging import logger


class MonitoringEngine:
    def __init__(self):
        self.watchlists: Dict[str, Watchlist] = {}
        self.alerts: List[Alert] = []
        self._initialize_default_watchlists()

    def _initialize_default_watchlists(self):
        default_items = [
            Watchlist(
                title="AI Models & Free Quotas",
                target_query="Gemini Claude OpenAI OpenRouter free tier quota changes",
                category="ai_models",
                check_interval_hours=12,
            ),
            Watchlist(
                title="1000hp Barra & TH400 Deals",
                target_query="Ford Falcon XR6 Turbo TH400 package Brisbane",
                category="automotive",
                check_interval_hours=12,
            ),
            Watchlist(
                title="RTX 4090 GPU Price Watch (Brisbane)",
                target_query="RTX 4090 used price drop Brisbane",
                category="electronics",
                check_interval_hours=6,
            ),
        ]
        for w in default_items:
            self.watchlists[w.watchlist_id] = w

    def add_watchlist(self, title: str, query: str, category: str, interval_hours: int = 12) -> Watchlist:
        wl = Watchlist(
            title=title,
            target_query=query,
            category=category,
            check_interval_hours=interval_hours,
            next_check=datetime.utcnow() + timedelta(hours=interval_hours),
        )
        self.watchlists[wl.watchlist_id] = wl
        return wl

    def get_all_watchlists(self) -> List[Watchlist]:
        return list(self.watchlists.values())

    def add_alert(self, alert: Alert):
        self.alerts.insert(0, alert)
        logger.info(f"[ALERT-{alert.significance}] {alert.title}: {alert.message}")
        try:
            import asyncio
            from researchos.packages.monitoring.webhooks import alert_dispatcher
            try:
                loop = asyncio.get_running_loop()
                loop.create_task(alert_dispatcher.dispatch(alert))
            except RuntimeError:
                pass
        except Exception as e:
            logger.debug(f"Webhook dispatch skipped: {e}")

    def get_recent_alerts(self, limit: int = 20) -> List[Alert]:
        return self.alerts[:limit]


monitoring_engine = MonitoringEngine()
