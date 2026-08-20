"""
ResearchOS Exa Neural Search API Connector
"""
from typing import List
import httpx
from researchos.packages.core.config import settings
from researchos.packages.core.logging import logger
from researchos.packages.core.schemas import SourceDocument, CredibilityTier, ProviderStatus
from researchos.packages.providers.base import BaseSearchProvider
from researchos.packages.security.policy import policy_enforcer


class ExaSearchProvider(BaseSearchProvider):
    def __init__(self, api_key: str = None):
        key = api_key or settings.EXA_API_KEY
        super().__init__(name="Exa", is_free=True, estimated_cost_aud=0.0)
        self.api_key = key
        self.endpoint = "https://api.exa.ai/search"

    async def check_health(self) -> ProviderStatus:
        if not self.api_key:
            self.status = ProviderStatus.UNAVAILABLE
            return ProviderStatus.UNAVAILABLE
        try:
            headers = {"x-api-key": self.api_key, "Content-Type": "application/json"}
            async with httpx.AsyncClient(timeout=8.0) as client:
                res = await client.post(self.endpoint, json={"query": "test", "numResults": 1}, headers=headers)
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
        headers = {"x-api-key": self.api_key, "Content-Type": "application/json"}
        payload = {
            "query": query,
            "numResults": max_results,
            "useAutoprompt": True,
            "contents": {"text": True},
        }

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.post(self.endpoint, json=payload, headers=headers)
                if resp.status_code == 200:
                    data = resp.json()
                    for item in data.get("results", []):
                        url = item.get("url", "")
                        title = item.get("title", "")
                        text = item.get("text", "")
                        snippet = text[:400] if text else title

                        results.append(
                            SourceDocument(
                                url=url,
                                canonical_url=url.split("?")[0],
                                title=title,
                                snippet=snippet,
                                raw_content=text,
                                provider_name=self.name,
                                credibility=CredibilityTier.SECONDARY,
                                published_date=item.get("publishedDate"),
                                author_or_domain=item.get("author", ""),
                            )
                        )
        except Exception as e:
            logger.error(f"Exa search error: {e}")

        return results
