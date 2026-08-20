"""
ResearchOS Base Provider Interfaces
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from researchos.packages.core.schemas import (
    ProviderType, ProviderStatus, SourceDocument, CredibilityTier
)


class BaseProvider(ABC):
    def __init__(self, name: str, provider_type: ProviderType, is_free: bool = True, estimated_cost_aud: float = 0.0):
        self.name = name
        self.provider_type = provider_type
        self.is_free = is_free
        self.estimated_cost_aud = estimated_cost_aud
        self.status = ProviderStatus.ONLINE
        self.latency_seconds = 0.0
        self.last_checked = None
        self.last_error = None
        self.quota_remaining: Optional[int] = None
        self.quota_total: Optional[int] = None

    @abstractmethod
    async def check_health(self) -> ProviderStatus:
        """Verifies connectivity, authentication, and quota availability."""
        pass


class BaseSearchProvider(BaseProvider):
    def __init__(self, name: str, is_free: bool = True, estimated_cost_aud: float = 0.0):
        super().__init__(name=name, provider_type=ProviderType.SEARCH, is_free=is_free, estimated_cost_aud=estimated_cost_aud)

    @abstractmethod
    async def search(self, query: str, max_results: int = 10, country: str = "AU") -> List[SourceDocument]:
        """Executes a search query and returns standardized SourceDocument list."""
        pass


class BaseAIProvider(BaseProvider):
    def __init__(self, name: str, is_free: bool = True, estimated_cost_aud: float = 0.0):
        super().__init__(name=name, provider_type=ProviderType.AI_MODEL, is_free=is_free, estimated_cost_aud=estimated_cost_aud)

    @abstractmethod
    async def generate_text(self, prompt: str, system_prompt: Optional[str] = None, model: Optional[str] = None, temperature: float = 0.2) -> str:
        """Generates text completion using the underlying model."""
        pass

    @abstractmethod
    async def list_available_models(self) -> List[Dict[str, Any]]:
        """Returns currently available models, identifying active free tiers."""
        pass
