"""
ResearchOS 12-Hour / Periodic Background Scheduler Engine
Runs continuous watchlists, detects price drops, quota shifts, and triggers alerts
"""
import asyncio
from datetime import datetime
from researchos.packages.core.logging import logger
from researchos.packages.core.config import settings
from researchos.packages.monitoring.watchlists import monitoring_engine
from researchos.packages.monitoring.differ import SnapshotDiffer
from researchos.packages.research.planner import ResearchPlanner
from researchos.packages.research.swarm import SearchSwarm


class ResearchScheduler:
    def __init__(self):
        self.is_running = False
        self.differ = SnapshotDiffer()
        self.planner = ResearchPlanner()
        self.swarm = SearchSwarm()
        self.cached_snapshots = {}

    async def start(self, check_loop_seconds: int = 60):
        self.is_running = True
        logger.info(f"ResearchOS Monitoring Scheduler started (Check interval: {check_loop_seconds}s)")

        while self.is_running:
            try:
                await self.check_due_watchlists()
            except Exception as e:
                logger.error(f"Scheduler execution cycle error: {e}")
            await asyncio.sleep(check_loop_seconds)

    async def check_due_watchlists(self):
        now = datetime.utcnow()
        watchlists = monitoring_engine.get_all_watchlists()

        for wl in watchlists:
            if not wl.is_active:
                continue

            # If check is due
            if wl.next_check is None or now >= wl.next_check:
                logger.info(f"[MONITOR-RUN] Checking watchlist '{wl.title}' ({wl.target_query})")
                plan = self.planner.create_plan(user_query=wl.target_query, mode=settings.OPERATING_MODE)
                swarm_res = await self.swarm.execute_swarm(plan)

                # Build snapshot
                prices = {}
                for l in swarm_res.get("listings", []):
                    if l.price_aud > 0:
                        prices[l.title[:30]] = l.price_aud

                items = [s.title for s in swarm_res.get("sources", [])[:10]]
                current_snapshot = {"prices": prices, "items": items, "quotas": {}}

                prev = self.cached_snapshots.get(wl.watchlist_id, {})
                alerts = self.differ.detect_changes(wl, prev, current_snapshot)

                for alert in alerts:
                    monitoring_engine.add_alert(alert)

                self.cached_snapshots[wl.watchlist_id] = current_snapshot
                wl.last_checked = now
                wl.next_check = now + asyncio.to_timedelta(hours=wl.check_interval_hours) if hasattr(asyncio, "to_timedelta") else None

    def stop(self):
        self.is_running = False


if __name__ == "__main__":
    scheduler = ResearchScheduler()
    asyncio.run(scheduler.start(check_loop_seconds=30))
