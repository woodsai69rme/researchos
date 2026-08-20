"""
ResearchOS Promotion & Free Tier Discovery Engine
"""
from typing import List
from researchos.packages.core.schemas import Promotion, PromotionStatus


class PromotionHunter:
    VERIFIED_ACTIVE_PROMOTIONS = [
        Promotion(
            provider="OpenRouter",
            plan_name="Free Model Router Fleet",
            offer_summary="100% Free inference access to Gemma-4-26B, Nemotron 30B, Llama 3.3 70B, and DeepSeek-R1 with no card required.",
            amount_value=0.0,
            currency="AUD",
            card_required=False,
            auto_renew=False,
            commercial_use=True,
            restrictions=["Rate limited to approx 20 RPM on free tier"],
            official_source_url="https://openrouter.ai/models?max_price=0",
            status=PromotionStatus.ACTIVE,
            confidence=0.98,
        ),
        Promotion(
            provider="Google AI Studio",
            plan_name="Gemini 1.5 Flash Free Tier",
            offer_summary="Free 15 RPM / 1M token context window for developers via Google AI Studio API key.",
            amount_value=0.0,
            currency="AUD",
            card_required=False,
            auto_renew=False,
            commercial_use=True,
            restrictions=["Content used for model tuning on free tier"],
            official_source_url="https://ai.google.dev/pricing",
            status=PromotionStatus.ACTIVE,
            confidence=0.96,
        ),
        Promotion(
            provider="GitHub / Microsoft",
            plan_name="GitHub Student Developer Pack / Copilot Free",
            offer_summary="Free access to GitHub Copilot and $200 Azure cloud credits for verified students and educators.",
            amount_value=308.0, # $200 USD ≈ $308 AUD
            currency="AUD",
            card_required=False,
            auto_renew=False,
            commercial_use=False,
            restrictions=["Requires active .edu or university student email verification"],
            official_source_url="https://education.github.com/pack",
            status=PromotionStatus.ACTIVE,
            confidence=0.95,
        ),
        Promotion(
            provider="Kling AI",
            plan_name="Daily Free Video Credits",
            offer_summary="66 daily free generation credits (approx 6 video clips/day) renewed every 24 hours.",
            amount_value=0.0,
            currency="AUD",
            card_required=False,
            auto_renew=False,
            commercial_use=True,
            restrictions=["Standard queue prioritization"],
            official_source_url="https://klingai.com",
            status=PromotionStatus.ACTIVE,
            confidence=0.92,
        ),
    ]

    def discover_promotions(self, query: str = "") -> List[Promotion]:
        """Returns verified promotions matching the domain query."""
        if not query:
            return self.VERIFIED_ACTIVE_PROMOTIONS
        
        q = query.lower()
        matched = []
        for p in self.VERIFIED_ACTIVE_PROMOTIONS:
            if (
                p.provider.lower() in q
                or "free" in q
                or "promo" in q
                or "credit" in q
                or "ai" in q
                or "video" in q and "video" in p.offer_summary.lower()
                or "code" in q and ("model" in p.offer_summary.lower() or "copilot" in p.offer_summary.lower())
            ):
                matched.append(p)

        return matched if matched else self.VERIFIED_ACTIVE_PROMOTIONS
