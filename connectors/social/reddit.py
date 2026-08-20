"""
ResearchOS Reddit Public Community Search Connector
"""
import urllib.parse
from typing import List
import httpx
from researchos.packages.core.logging import logger
from researchos.packages.core.schemas import SourceDocument, CredibilityTier


class RedditConnector:
    def __init__(self):
        self.base_url = "https://www.reddit.com/search.json"
        self.headers = {"User-Agent": "ResearchOS-Discovery-Bot/1.0 (Windows 11)"}

    async def search_discussions(self, query: str, max_results: int = 10, subreddit: str = None) -> List[SourceDocument]:
        results: List[SourceDocument] = []
        target_url = f"https://www.reddit.com/r/{subreddit}/search.json" if subreddit else self.base_url
        params = {"q": query, "sort": "relevance", "limit": max_results, "restrict_sr": "1" if subreddit else "0"}

        try:
            async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
                resp = await client.get(target_url, headers=self.headers, params=params)
                if resp.status_code == 200:
                    data = resp.json()
                    children = data.get("data", {}).get("children", [])
                    for child in children:
                        post = child.get("data", {})
                        title = post.get("title", "")
                        permalink = post.get("permalink", "")
                        selftext = post.get("selftext", "")[:400]
                        sub = post.get("subreddit", "")
                        score = post.get("score", 0)
                        num_comments = post.get("num_comments", 0)
                        full_url = f"https://reddit.com{permalink}"

                        snippet = f"r/{sub} | Score: {score} | Comments: {num_comments}\n{selftext or title}"

                        results.append(
                            SourceDocument(
                                url=full_url,
                                canonical_url=full_url,
                                title=f"Reddit: {title}",
                                snippet=snippet,
                                provider_name="Reddit",
                                credibility=CredibilityTier.COMMUNITY,
                                author_or_domain=f"r/{sub}",
                                metadata={"score": score, "comments": num_comments, "subreddit": sub},
                            )
                        )
        except Exception as e:
            logger.error(f"Reddit search failed for '{query}': {e}")

        return results
