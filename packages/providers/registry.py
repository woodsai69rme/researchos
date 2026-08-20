"""
ResearchOS Provider Registry, Health Monitoring & Dynamic Verification
"""
from datetime import datetime
from typing import Dict, List, Optional
from researchos.packages.core.logging import logger
from researchos.packages.core.schemas import ProviderStatus, ProviderType
from researchos.packages.providers.base import BaseAIProvider, BaseProvider, BaseSearchProvider
from researchos.connectors.search.duckduckgo import DuckDuckGoSearchProvider
from researchos.connectors.search.googlenews import GoogleNewsRSSProvider
from researchos.connectors.search.brave import BraveSearchProvider
from researchos.connectors.search.tavily import TavilySearchProvider
from researchos.connectors.search.exa import ExaSearchProvider
from researchos.connectors.search.serper import SerperSearchProvider
from researchos.connectors.ai.ollama import OllamaAIProvider
from researchos.connectors.ai.openrouter import OpenRouterAIProvider
from researchos.connectors.ai.gemini import GeminiAIProvider


class ProviderRegistry:
    def __init__(self):
        self.search_providers: Dict[str, BaseSearchProvider] = {}
        self.ai_providers: Dict[str, BaseAIProvider] = {}
        self._initialize_default_providers()

    def _initialize_default_providers(self):
        # Register Search Providers (Free-first priority order)
        self.register_search_provider(DuckDuckGoSearchProvider())
        self.register_search_provider(GoogleNewsRSSProvider())
        self.register_search_provider(BraveSearchProvider())
        self.register_search_provider(TavilySearchProvider())
        self.register_search_provider(ExaSearchProvider())
        self.register_search_provider(SerperSearchProvider())

        # Register AI Providers
        self.register_ai_provider(OllamaAIProvider())
        self.register_ai_provider(OpenRouterAIProvider())
        self.register_ai_provider(GeminiAIProvider())

    def register_search_provider(self, provider: BaseSearchProvider):
        self.search_providers[provider.name] = provider

    def register_ai_provider(self, provider: BaseAIProvider):
        self.ai_providers[provider.name] = provider

    def get_search_provider(self, name: str) -> Optional[BaseSearchProvider]:
        return self.search_providers.get(name)

    def get_ai_provider(self, name: str) -> Optional[BaseAIProvider]:
        return self.ai_providers.get(name)

    async def get_active_search_providers(self, free_only: bool = True) -> List[BaseSearchProvider]:
        active = []
        for p in self.search_providers.values():
            if free_only and not p.is_free:
                continue
            status = await p.check_health()
            if status in (ProviderStatus.ONLINE, ProviderStatus.DEGRADED):
                active.append(p)
        return active

    async def get_best_available_ai_provider(self, prefer_local: bool = False) -> Optional[BaseAIProvider]:
        # Priority: Local Ollama (if running) -> OpenRouter Free -> Gemini Free
        if prefer_local:
            ollama = self.ai_providers.get("OllamaLocal")
            if ollama and await ollama.check_health() == ProviderStatus.ONLINE:
                return ollama

        for name in ["OpenRouter", "GoogleGemini", "OllamaLocal"]:
            provider = self.ai_providers.get(name)
            if provider:
                status = await provider.check_health()
                if status == ProviderStatus.ONLINE:
                    return provider
                
        # Fallback to any online AI provider
        for provider in self.ai_providers.values():
            if await provider.check_health() in (ProviderStatus.ONLINE, ProviderStatus.DEGRADED):
                return provider
        return None

    async def get_all_provider_health(self) -> List[Dict]:
        health_list = []
        all_providers: List[BaseProvider] = list(self.search_providers.values()) + list(self.ai_providers.values())
        for p in all_providers:
            status = await p.check_health()
            health_list.append({
                "name": p.name,
                "type": p.provider_type.value,
                "status": status.value,
                "is_free": p.is_free,
                "estimated_cost_aud": p.estimated_cost_aud,
                "last_checked": datetime.utcnow().isoformat(),
            })
        return health_list


provider_registry = ProviderRegistry()
