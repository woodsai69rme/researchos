"""
ResearchOS Serper.dev Google Search API Connector
"""
from typing import List
import httpx
from researchos.packages.core.config import settings
from researchos.packages.core.logging import logger
from researchos.packages.core.schemas import SourceDocument, CredibilityTier, ProviderStatus
from researchos.packages.providers.base import BaseSearchProvider
from researchos.packages.security.policy import policy_enforcer


class SerperSearchProvider(BaseSearchProvider):
    def __init__(self, api_key: str = None):
        key = api_key or settings.SERPER_API_KEY
        super().__init__(name="Serper", is_free=True, estimated_cost_aud=0.0)
        self.api_key = key
        self.endpoint = "https://google.serper.dev/search"

    async def check_health(self) -> ProviderStatus:
        if not self.api_key:
            self.status = ProviderStatus.UNAVAILABLE
            return ProviderStatus.UNAVAILABLE
        try:
            headers = {"X-API-KEY": self.api_key, "Content-Type": "application/json"}
            async with httpx.AsyncClient(timeout=8.0) as client:
                res = await client.post(self.endpoint, json={"q": "test", "num": 1}, headers=headers)
                if res.status_code == 200:
                    self.status = ProviderStatus.ONLINE
                elif res.status_code == 429:
                    self.status = ProviderStatus.RATE_LIMITED
                elif res.status_code in (401, 403):
                    self.status = ProviderStatus.AUTH_ERROR
                else:
                    self.status = ProviderStatus.DEGRADED
        except Exception:
            self.status = ProviderStatus.UNAVAILABLE
        return self.status

    async def search(self, query: str, max_results: int = 10, country: str = "AU") -> List[SourceDocument]:
        if not self.api_key:
            return []

        policy_enforcer.authorize_execution(self.name, self.is_free, self.estimated_cost_aud)
        results: List[SourceDocument] = []
        headers = {"X-API-KEY": self.api_key, "Content-Type": "application/json"}
        payload = {
            "q": query,
            "gl": country.lower(),
            "hl": "en",
            "num": max_results,
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.post(self.endpoint, json=payload, headers=headers)
                if resp.status_code == 200:
                    data = resp.json()
                    for item in data.get("organic", []):
                        url = item.get("link", "")
                        title = item.get("title", "")
                        snippet = item.get("snippet", "")

                        results.append(
                            SourceDocument(
                                url=url,
                                canonical_url=url.split("?")[0],
                                title=title,
                                snippet=snippet,
                                provider_name=self.name,
                                credibility=CredibilityTier.SECONDARY,
                            )
                        )
        except Exception as e:
            logger.error(f"Serper search error: {e}")

        return results
