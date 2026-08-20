"""
ResearchOS GitHub Open-Source Ecosystem & Release Connector
"""
from typing import Any, Dict, List, Optional
import httpx
from researchos.packages.core.config import settings
from researchos.packages.core.logging import logger
from researchos.packages.core.schemas import SourceDocument, CredibilityTier


class GitHubConnector:
    def __init__(self, token: Optional[str] = None):
        self.token = token or settings.GITHUB_TOKEN
        self.base_url = "https://api.github.com"
        self.headers = {"Accept": "application/vnd.github.v3+json", "User-Agent": "ResearchOS-Agent"}
        if self.token:
            self.headers["Authorization"] = f"token {self.token}"

    async def search_repositories(self, query: str, max_results: int = 10) -> List[SourceDocument]:
        results: List[SourceDocument] = []
        url = f"{self.base_url}/search/repositories"
        params = {"q": query, "sort": "stars", "order": "desc", "per_page": min(max_results, 30)}

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(url, headers=self.headers, params=params)
                if resp.status_code == 200:
                    items = resp.json().get("items", [])
                    for item in items:
                        name = item.get("full_name", "")
                        html_url = item.get("html_url", "")
                        desc = item.get("description", "") or ""
                        stars = item.get("stargazers_count", 0)
                        license_name = item.get("license", {}).get("name", "Unknown License") if item.get("license") else "No License"
                        topics = ", ".join(item.get("topics", []))

                        snippet = f"Repo: {name} | Stars: {stars:,} | License: {license_name} | Topics: {topics}\n{desc}"

                        results.append(
                            SourceDocument(
                                url=html_url,
                                canonical_url=html_url,
                                title=f"GitHub - {name}",
                                snippet=snippet,
                                provider_name="GitHub",
                                credibility=CredibilityTier.PRIMARY,
                                author_or_domain=name.split("/")[0],
                                metadata={"stars": stars, "license": license_name, "forks": item.get("forks_count", 0)},
                            )
                        )
        except Exception as e:
            logger.error(f"GitHub search failed: {e}")

        return results
