"""
ResearchOS Empire Bridge
Connects ResearchOS Intelligence to Tellem Studio OS and Crypto Top Buyer Radar
"""
import json
import os
import sys
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any

base_dir = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(base_dir))
sys.path.insert(0, str(base_dir.parent))
os.environ["PYTHONPATH"] = str(base_dir.parent)

from researchos.packages.core.logging import logger
from researchos.packages.models.catalog import model_catalog
from researchos.packages.pricing.video_costs import video_cost_engine


class EmpireBridge:
    def __init__(self):
        self.output_dir = base_dir / "data" / "empire_feeds"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.tellem_sync_file = self.output_dir / "tellem_studio_feed.json"
        self.crypto_sync_file = self.output_dir / "crypto_radar_feed.json"

    def export_tellem_studio_feed(self) -> Path:
        """
        Exports the latest AI video model pricing (Wan 2.2 vs Kling 3.0 vs Hailuo 2.3)
        and model rankings for Tellem Studio's automated video pipeline.
        """
        models = model_catalog.get_models(free_only=True)
        video_costs = video_cost_engine.calculate_all_costs(music_video_minutes=3.5)

        feed_data = {
            "source": "ResearchOS",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "recommended_local_video_engine": "Wan 2.2 Mega (Local ComfyUI)",
            "local_clip_cost_aud": 0.0,
            "commercial_cloud_fallbacks": [
                {
                    "provider": c.provider_name,
                    "model": c.model_name,
                    "resolution": c.max_resolution,
                    "estimated_total_mv_cost_aud": c.estimated_total_music_video_cost_aud,
                    "free_generations_monthly": c.free_generations_monthly,
                }
                for c in video_costs[:3]
            ],
            "recommended_coding_llms": [
                {
                    "id": m.model_id,
                    "name": m.model_name,
                    "swe_bench": m.coding_score_swe_bench,
                    "context": m.context_window,
                    "provider": m.provider,
                }
                for m in models[:4]
            ],
        }

        with open(self.tellem_sync_file, "w", encoding="utf-8") as f:
            json.dump(feed_data, f, indent=2)

        logger.info(f"[EMPIRE-BRIDGE] Tellem Studio Feed exported to: {self.tellem_sync_file}")
        return self.tellem_sync_file

    def export_crypto_radar_feed(self) -> Path:
        """
        Exports macro hardware and computing costs (GPU price trends, token costs)
        for correlation with AI-token & crypto macro volume in the Top Buyer Radar.
        """
        feed_data = {
            "source": "ResearchOS",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "hardware_arbitrage_benchmark": {
                "asset": "NVIDIA GeForce RTX 4090 24GB",
                "target_buy_threshold_aud": 1850.0,
                "median_retail_aud": 2400.0,
                "currency": "AUD",
                "location": "Brisbane, Queensland, Australia",
            },
            "openrouter_free_status": {
                "operating_mode": "FREE_ONLY",
                "verified_spend_aud": 0.0,
                "active_zero_cost_endpoints": 12,
            },
        }

        with open(self.crypto_sync_file, "w", encoding="utf-8") as f:
            json.dump(feed_data, f, indent=2)

        logger.info(f"[EMPIRE-BRIDGE] Crypto Radar Feed exported to: {self.crypto_sync_file}")
        return self.crypto_sync_file

    def sync_all(self) -> Dict[str, str]:
        t_path = self.export_tellem_studio_feed()
        c_path = self.export_crypto_radar_feed()
        return {
            "tellem_feed": str(t_path),
            "crypto_feed": str(c_path),
        }


empire_bridge = EmpireBridge()

if __name__ == "__main__":
    res = empire_bridge.sync_all()
    print("[OK] Empire Bridge synchronization complete:")
    print("     Tellem Feed: ", res["tellem_feed"])
    print("     Crypto Feed: ", res["crypto_feed"])
