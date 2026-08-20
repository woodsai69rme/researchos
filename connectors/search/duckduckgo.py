"""
ResearchOS DuckDuckGo 100% Free Native Search Connector
"""
import asyncio
import re
import urllib.parse
from typing import List
import httpx
from bs4 import BeautifulSoup
from researchos.packages.core.logging import logger
from researchos.packages.core.schemas import SourceDocument, CredibilityTier, ProviderStatus
from researchos.packages.providers.base import BaseSearchProvider
from researchos.packages.security.policy import policy_enforcer


class DuckDuckGoSearchProvider(BaseSearchProvider):
    def __init__(self):
        super().__init__(name="DuckDuckGo", is_free=True, estimated_cost_aud=0.0)
        self.base_url = "https://html.duckduckgo.com/html/"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
            "Accept-Language": "en-AU,en;q=0.9",
        }

    async def check_health(self) -> ProviderStatus:
        try:
            async with httpx.AsyncClient(timeout=8.0) as client:
                res = await client.get("https://html.duckduckgo.com/html/?q=test", headers=self.headers)
                if res.status_code == 200:
                    self.status = ProviderStatus.ONLINE
                    return ProviderStatus.ONLINE
                elif res.status_code == 429:
                    self.status = ProviderStatus.RATE_LIMITED
                    return ProviderStatus.RATE_LIMITED
        except Exception as e:
            logger.warning(f"DuckDuckGo health check error: {e}")
            self.status = ProviderStatus.DEGRADED
        return self.status

    async def search(self, query: str, max_results: int = 10, country: str = "AU") -> List[SourceDocument]:
        policy_enforcer.authorize_execution(self.name, self.is_free, self.estimated_cost_aud)
        results: List[SourceDocument] = []
        
        # Format region for Australia if requested
        kl_region = "au-en" if country.upper() == "AU" else "wt-wt"
        data = {"q": query, "kl": kl_region}

        try:
            async with httpx.AsyncClient(headers=self.headers, timeout=12.0, follow_redirects=True) as client:
                resp = await client.post(self.base_url, data=data)
                if resp.status_code != 200:
                    logger.warning(f"DuckDuckGo search returned status {resp.status_code}")
                    return results

                soup = BeautifulSoup(resp.text, "html.parser")
                web_results = soup.find_all("div", class_="web-result") or soup.find_all("div", class_="result")

                for item in web_results:
                    if len(results) >= max_results:
                        break

                    title_elem = item.find("a", class_="result__a") or item.find("h2")
                    snippet_elem = item.find("a", class_="result__snippet") or item.find("div", class_="result__snippet")
                    
                    if not title_elem:
                        continue

                    title = title_elem.get_text(strip=True)
                    raw_url = title_elem.get("href", "")

                    # DuckDuckGo wraps URLs in /l/?uddg=...
                    if "/l/?uddg=" in raw_url:
                        try:
                            parsed = urllib.parse.urlparse(raw_url)
                            query_params = urllib.parse.parse_qs(parsed.query)
                            url = query_params.get("uddg", [raw_url])[0]
                        except Exception:
                            url = raw_url
                    else:
                        url = raw_url

                    snippet = snippet_elem.get_text(strip=True) if snippet_elem else ""

                    if not url.startswith("http"):
                        continue

                    # Credibility assignment
                    domain = urllib.parse.urlparse(url).netloc.lower()
                    credibility = CredibilityTier.SECONDARY
                    if any(tld in domain for tld in [".gov.au", ".edu.au", "github.com", "microsoft.com", "google.com", "ford.com"]):
                        credibility = CredibilityTier.PRIMARY
                    elif any(c_dom in domain for c_dom in ["reddit.com", "youtube.com", "whirlpool.net.au", "boostcruising.com", "fordforums.com.au"]):
                        credibility = CredibilityTier.COMMUNITY

                    results.append(
                        SourceDocument(
                            url=url,
                            canonical_url=url.split("?")[0],
                            title=title,
                            snippet=snippet,
                            provider_name=self.name,
                            credibility=credibility,
                            author_or_domain=domain,
                        )
                    )

        except Exception as e:
            logger.error(f"DuckDuckGo search failure for '{query}': {e}")

        return results
