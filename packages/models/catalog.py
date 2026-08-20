"""
ResearchOS Verified AI Model & SWE-Bench Coding Catalog
"""
from typing import List, Optional
from researchos.packages.core.schemas import ModelSpec


class ModelCatalog:
    VERIFIED_MODELS = [
        ModelSpec(
            model_id="ornith-1.0-35b:q4_k_m",
            provider="Local Ollama / HuggingFace",
            model_name="Ornith 1.0 35B (MoE)",
            version="1.0",
            context_window=262144,
            max_output_tokens=8192,
            modalities=["text", "code"],
            tool_use_supported=True,
            reasoning_supported=True,
            coding_score_swe_bench=75.6,
            is_open_weights=True,
            is_local_capable=True,
            recommended_vram_gb=21.0,
            is_free_tier_available=True,
            free_limits_description="100% Free offline local execution via Ollama + --n-cpu-moe offload",
            price_per_m_input_usd=0.0,
            price_per_m_output_usd=0.0,
            effective_cost_aud=0.0,
            latency_seconds_approx=4.5,
        ),
        ModelSpec(
            model_id="ornith-1.0-9b:q4_k_m",
            provider="Local Ollama / HuggingFace",
            model_name="Ornith 1.0 9B (Dense)",
            version="1.0",
            context_window=262144,
            max_output_tokens=8192,
            modalities=["text", "code"],
            tool_use_supported=True,
            reasoning_supported=True,
            coding_score_swe_bench=69.4,
            is_open_weights=True,
            is_local_capable=True,
            recommended_vram_gb=5.6,
            is_free_tier_available=True,
            free_limits_description="100% Free offline local execution fitting entirely in 8GB RTX 4060 VRAM",
            price_per_m_input_usd=0.0,
            price_per_m_output_usd=0.0,
            effective_cost_aud=0.0,
            latency_seconds_approx=1.8,
        ),
        ModelSpec(
            model_id="google/gemma-4-26b-a4b-it:free",
            provider="OpenRouter Free Tier",
            model_name="Gemma 4 26B A4B Instruct",
            version="4.0",
            context_window=131072,
            max_output_tokens=8192,
            modalities=["text", "code", "vision"],
            vision_supported=True,
            tool_use_supported=True,
            reasoning_supported=True,
            coding_score_swe_bench=68.2,
            is_open_weights=True,
            is_local_capable=False,
            is_free_tier_available=True,
            free_limits_description="100% Free cloud inference on OpenRouter with sub-3s response time",
            price_per_m_input_usd=0.0,
            price_per_m_output_usd=0.0,
            effective_cost_aud=0.0,
            latency_seconds_approx=2.7,
        ),
        ModelSpec(
            model_id="qwen2.5-coder:latest",
            provider="Local Ollama / Alibaba",
            model_name="Qwen 2.5 Coder 7B",
            version="2.5",
            context_window=131072,
            max_output_tokens=8192,
            modalities=["text", "code"],
            tool_use_supported=True,
            coding_score_swe_bench=62.5,
            is_open_weights=True,
            is_local_capable=True,
            recommended_vram_gb=4.7,
            is_free_tier_available=True,
            free_limits_description="100% Free local 40+ tok/s coding fallback on 8GB VRAM",
            price_per_m_input_usd=0.0,
            price_per_m_output_usd=0.0,
            effective_cost_aud=0.0,
            latency_seconds_approx=1.2,
        ),
        ModelSpec(
            model_id="deepseek-r1:8b",
            provider="Local Ollama / DeepSeek",
            model_name="DeepSeek R1 Distill 8B",
            version="1.0",
            context_window=131072,
            max_output_tokens=8192,
            modalities=["text", "code"],
            tool_use_supported=False,
            reasoning_supported=True,
            coding_score_swe_bench=64.1,
            is_open_weights=True,
            is_local_capable=True,
            recommended_vram_gb=5.2,
            is_free_tier_available=True,
            free_limits_description="100% Free Chain-of-Thought reasoning for code analysis and bug fixing",
            price_per_m_input_usd=0.0,
            price_per_m_output_usd=0.0,
            effective_cost_aud=0.0,
            latency_seconds_approx=3.1,
        ),
    ]

    def get_models(self, category: str = "all", free_only: bool = True) -> List[ModelSpec]:
        models = self.VERIFIED_MODELS
        if free_only:
            models = [m for m in models if m.is_free_tier_available]
        
        # Sort by SWE-Bench coding score descending
        models.sort(key=lambda x: x.coding_score_swe_bench or 0.0, reverse=True)
        return models


model_catalog = ModelCatalog()
