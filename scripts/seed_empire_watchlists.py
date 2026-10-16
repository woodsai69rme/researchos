"""
ResearchOS Production Watchlists & Cross-System Automation Seeder
Registers high-alpha watchlists and triggers initial snapshot runs
"""
import sys
import os
import asyncio
from pathlib import Path

base_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(base_dir))
sys.path.insert(0, str(base_dir.parent))
os.environ["PYTHONPATH"] = str(base_dir.parent)

from researchos.packages.monitoring.watchlists import monitoring_engine
from researchos.apps.scheduler.scheduler import ResearchScheduler


async def run_seeder_and_monitor():
    print("============================================================")
    print(" ResearchOS Active Watchlists & Initial Scan Cycle")
    print("============================================================")
    
    # Register production watchlists
    wl1 = monitoring_engine.add_watchlist(
        title="RTX 4090 GPU Arbitrage Radar (QLD/AU)",
        query="RTX 4090 24GB graphics card Brisbane Queensland Australia Gumtree CeX Cash Converters",
        category="electronics",
        interval_hours=6,
    )
    print(f"[OK] Registered Watchlist: [{wl1.watchlist_id[:8]}] {wl1.title}")

    wl2 = monitoring_engine.add_watchlist(
        title="Ford Falcon Barra Turbo TH400 Package (Brisbane/QLD)",
        query="Ford Falcon XR6 Turbo Barra 4.0L TH400 transmission conversion package Brisbane",
        category="automotive",
        interval_hours=12,
    )
    print(f"[OK] Registered Watchlist: [{wl2.watchlist_id[:8]}] {wl2.title}")

    wl3 = monitoring_engine.add_watchlist(
        title="Zero-Cost AI Coding & Video Models Radar",
        query="OpenRouter free models SWE-bench coding Ollama Wan 2.2 Kling releases",
        category="ai_models",
        interval_hours=12,
    )
    print(f"[OK] Registered Watchlist: [{wl3.watchlist_id[:8]}] {wl3.title}")

    all_wl = monitoring_engine.get_all_watchlists()
    print(f"\n[+] Total Active Watchlists in Engine: {len(all_wl)}")

    print("\n[*] Triggering immediate scan cycle across all active watchlists...")
    scheduler = ResearchScheduler()
    # Force next_check to now for immediate processing
    for w in all_wl:
        w.next_check = None

    await scheduler.check_due_watchlists()
    print("[OK] Initial monitoring scan cycle complete! Snapshots cached.")
    print("============================================================\n")


if __name__ == "__main__":
    asyncio.run(run_seeder_and_monitor())
