"""
ResearchOS AI Video Generation Cost & Tier Calculator
Compares Wan 2.2, Kling, Hailuo, Runway Gen-3, Luma Dream Machine, Sora, and Veo
"""
from typing import List
from researchos.packages.core.schemas import VideoProviderCost
from researchos.packages.pricing.currency import currency_converter


class VideoCostEngine:
    KNOWN_VIDEO_PROVIDERS = [
        {
            "provider": "Wan 2.2 Mega (Local ComfyUI)",
            "model": "wan2.2-rapid-mega-aio-nsfw-v12.2.safetensors",
            "free_daily": 999,
            "free_monthly": 9999,
            "clip_length_s": 5,
            "res": "512x512 / 720p",
            "watermark": False,
            "commercial": True,
            "sub_usd": 0.0,
            "cost_per_clip_usd": 0.0,
        },
        {
            "provider": "Kling AI (Kuaishou)",
            "model": "Kling 1.5 Pro",
            "free_daily": 6,
            "free_monthly": 180,
            "clip_length_s": 5,
            "res": "720p / 1080p",
            "watermark": False,
            "commercial": True,
            "sub_usd": 10.0,
            "cost_per_clip_usd": 0.15,
        },
        {
            "provider": "Minimax Hailuo AI",
            "model": "Hailuo Video-01",
            "free_daily": 5,
            "free_monthly": 150,
            "clip_length_s": 6,
            "res": "720p",
            "watermark": False,
            "commercial": True,
            "sub_usd": 12.0,
            "cost_per_clip_usd": 0.20,
        },
        {
            "provider": "Runway Gen-3 Alpha",
            "model": "Gen-3 Alpha Turbo",
            "free_daily": 0,
            "free_monthly": 25,
            "clip_length_s": 10,
            "res": "720p / 1080p",
            "watermark": False,
            "commercial": True,
            "sub_usd": 15.0,
            "cost_per_clip_usd": 0.50,
        },
        {
            "provider": "Luma Dream Machine",
            "model": "Dream Machine 1.5",
            "free_daily": 1,
            "free_monthly": 30,
            "clip_length_s": 5,
            "res": "720p",
            "watermark": True,
            "commercial": False,
            "sub_usd": 29.99,
            "cost_per_clip_usd": 0.60,
        },
        {
            "provider": "Google Veo (YouTube Shorts / Vertex)",
            "model": "Veo 2",
            "free_daily": 3,
            "free_monthly": 90,
            "clip_length_s": 6,
            "res": "1080p",
            "watermark": False,
            "commercial": True,
            "sub_usd": 0.0,
            "cost_per_clip_usd": 0.35,
        }
    ]

    def calculate_all_costs(self, music_video_minutes: float = 3.5) -> List[VideoProviderCost]:
        """Calculates exact AUD costs, clips required, and costs per minute for music videos."""
        total_seconds = music_video_minutes * 60
        costs: List[VideoProviderCost] = []

        for p in self.KNOWN_VIDEO_PROVIDERS:
            clip_len = p["clip_length_s"]
            clips_needed = int(total_seconds // clip_len) + 4 # add buffer clips

            sub_aud = currency_converter.to_aud(p["sub_usd"])
            cost_per_clip_aud = currency_converter.to_aud(p["cost_per_clip_usd"])
            cost_per_min_aud = round((cost_per_clip_aud / clip_len) * 60, 2)
            total_mv_cost_aud = round(clips_needed * cost_per_clip_aud, 2)

            costs.append(
                VideoProviderCost(
                    provider_name=p["provider"],
                    model_name=p["model"],
                    free_generations_daily=p["free_daily"],
                    free_generations_monthly=p["free_monthly"],
                    generation_length_seconds=clip_len,
                    max_resolution=p["res"],
                    has_watermark=p["watermark"],
                    commercial_use_allowed=p["commercial"],
                    subscription_cost_monthly_aud=sub_aud,
                    credit_cost_per_clip_aud=cost_per_clip_aud,
                    cost_per_minute_aud=cost_per_min_aud,
                    estimated_music_video_clips=clips_needed,
                    estimated_total_music_video_cost_aud=total_mv_cost_aud,
                )
            )

        # Sort: lowest music video total cost first (Local Wan 2.2 = $0.00 first)
        costs.sort(key=lambda x: x.estimated_total_music_video_cost_aud)
        return costs
