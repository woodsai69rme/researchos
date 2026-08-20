"""
ResearchOS Brave Search API Connector
"""
from typing import List
import httpx
from researchos.packages.core.config import settings
from researchos.packages.core.logging import logger
from researchos.packages.core.schemas import SourceDocument, CredibilityTier, ProviderStatus
from researchos.packages.providers.base import BaseSearchProvider
from researchos.packages.security.policy import policy_enforcer


class BraveSearchProvider(BaseSearchProvider):
    def __init__(self, api_key: str = None):
        key = api_key or settings.BRAVE_API_KEY
        # Brave provides a free tier allowance (2000 queries/month free)
        super().__init__(name="BraveSearch", is_free=True, estimated_cost_aud=0.0)
        self.api_key = key
        self.endpoint = "https://api.search.brave.com/res/v1/web/search"

    async def check_health(self) -> ProviderStatus:
        if not self.api_key:
            self.status = ProviderStatus.UNAVAILABLE
            return ProviderStatus.UNAVAILABLE
        try:
            headers = {"Accept": "application/json", "X-Subscription-Token": self.api_key}
            async with httpx.AsyncClient(timeout=8.0) as client:
                res = await client.get(f"{self.endpoint}?q=ping&count=1", headers=headers)
                if res.status_code == 200:
                    self.status = ProviderStatus.ONLINE
                elif res.status_code == 429:
                    self.status = ProviderStatus.RATE_LIMITED
                elif res.status_code in (401, 403):
                    self.status = ProviderStatus.AUTH_ERROR
                else:
                    self.status = ProviderStatus.DEGRADED
        except Exception as e:
            logger.warning(f"Brave health check failed: {e}")
            self.status = ProviderStatus.UNAVAILABLE
        return self.status

    async def search(self, query: str, max_results: int = 10, country: str = "AU") -> List[SourceDocument]:
        if not self.api_key:
            logger.debug("Brave API Key not configured; skipping.")
            return []

        policy_enforcer.authorize_execution(self.name, self.is_free, self.estimated_cost_aud)
        results: List[SourceDocument] = []
        headers = {
            "Accept": "application/json",
            "X-Subscription-Token": self.api_key,
        }
        params = {
            "q": query,
            "count": min(max_results, 20),
            "country": country.lower(),
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(self.endpoint, headers=headers, params=params)
                if resp.status_code == 200:
                    data = resp.json()
                    web_results = data.get("web", {}).get("results", [])
                    for item in web_results:
                        url = item.get("url", "")
                        title = item.get("title", "")
                        snippet = item.get("description", "")
                        domain = item.get("profile", {}).get("name", "")

                        results.append(
                            SourceDocument(
                                url=url,
                                canonical_url=url.split("?")[0],
                                title=title,
                                snippet=snippet,
                                provider_name=self.name,
                                credibility=CredibilityTier.SECONDARY,
                                author_or_domain=domain,
                            )
                        )
                elif resp.status_code == 429:
                    self.status = ProviderStatus.RATE_LIMITED
                    logger.warning("Brave search rate limit exceeded.")
        except Exception as e:
            logger.error(f"Brave search error: {e}")

        return results
