"""
ResearchOS YouTube Public Video & Transcript Connector
"""
import re
import urllib.parse
from typing import List
import httpx
from researchos.packages.core.logging import logger
from researchos.packages.core.schemas import SourceDocument, CredibilityTier


class YouTubeConnector:
    def __init__(self):
        self.search_url = "https://www.youtube.com/results"
        self.headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

    async def search_videos(self, query: str, max_results: int = 8) -> List[SourceDocument]:
        results: List[SourceDocument] = []
        encoded = urllib.parse.quote(query)
        url = f"{self.search_url}?search_query={encoded}"

        try:
            async with httpx.AsyncClient(timeout=10.0, headers=self.headers) as client:
                resp = await client.get(url)
                if resp.status_code == 200:
                    text = resp.text
                    # Extract video ids from YouTube initialData blob
                    video_ids = list(set(re.findall(r"\"videoId\":\"([a-zA-Z0-9_-]{11})\"", text)))
                    titles = re.findall(r"\"title\":\{\"runs\":\[\{\"text\":\"(.*?)\"\}\]", text)

                    for idx, vid in enumerate(video_ids[:max_results]):
                        v_title = titles[idx] if idx < len(titles) else f"YouTube Video {vid}"
                        v_url = f"https://www.youtube.com/watch?v={vid}"
                        results.append(
                            SourceDocument(
                                url=v_url,
                                canonical_url=v_url,
                                title=f"YouTube: {v_title}",
                                snippet=f"YouTube Video Review/Walkthrough: {v_title} ({v_url})",
                                provider_name="YouTube",
                                credibility=CredibilityTier.COMMUNITY,
                                author_or_domain="YouTube",
                            )
                        )
        except Exception as e:
            logger.error(f"YouTube search error: {e}")

        return results
