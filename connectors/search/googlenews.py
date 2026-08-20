"""
ResearchOS Google News Free RSS Search Connector
"""
import urllib.parse
from typing import List
import httpx
from bs4 import BeautifulSoup
from researchos.packages.core.logging import logger
from researchos.packages.core.schemas import SourceDocument, CredibilityTier, ProviderStatus
from researchos.packages.providers.base import BaseSearchProvider
from researchos.packages.security.policy import policy_enforcer


class GoogleNewsRSSProvider(BaseSearchProvider):
    def __init__(self):
        super().__init__(name="GoogleNewsRSS", is_free=True, estimated_cost_aud=0.0)
        self.base_url = "https://news.google.com/rss/search"

    async def check_health(self) -> ProviderStatus:
        try:
            async with httpx.AsyncClient(timeout=8.0) as client:
                res = await client.get(f"{self.base_url}?q=Australia&hl=en-AU&gl=AU&ceid=AU:en")
                if res.status_code == 200:
                    self.status = ProviderStatus.ONLINE
                    return ProviderStatus.ONLINE
        except Exception:
            self.status = ProviderStatus.DEGRADED
        return self.status

    async def search(self, query: str, max_results: int = 10, country: str = "AU") -> List[SourceDocument]:
        policy_enforcer.authorize_execution(self.name, self.is_free, self.estimated_cost_aud)
        results: List[SourceDocument] = []
        encoded_query = urllib.parse.quote(query)
        url = f"{self.base_url}?q={encoded_query}&hl=en-AU&gl=AU&ceid=AU:en"

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(url)
                if resp.status_code != 200:
                    return results

                soup = BeautifulSoup(resp.content, "xml")
                items = soup.find_all("item")

                for item in items:
                    if len(results) >= max_results:
                        break
                    title = item.title.text if item.title else ""
                    link = item.link.text if item.link else ""
                    pub_date = item.pubDate.text if item.pubDate else ""
                    description = item.description.text if item.description else ""
                    
                    # Clean html from description
                    clean_desc = BeautifulSoup(description, "html.parser").get_text(strip=True) if description else ""

                    if not link:
                        continue

                    results.append(
                        SourceDocument(
                            url=link,
                            canonical_url=link,
                            title=title,
                            snippet=clean_desc or title,
                            provider_name=self.name,
                            credibility=CredibilityTier.SECONDARY,
                            published_date=pub_date,
                            author_or_domain="Google News",
                        )
                    )
        except Exception as e:
            logger.error(f"Google News RSS search failure: {e}")

        return results
