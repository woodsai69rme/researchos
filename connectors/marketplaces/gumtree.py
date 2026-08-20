"""
ResearchOS Gumtree Australia Marketplace Connector
"""
import re
import urllib.parse
from typing import List
import httpx
from bs4 import BeautifulSoup
from researchos.packages.core.logging import logger
from researchos.packages.core.schemas import MarketplaceListing


class GumtreeAUConnector:
    def __init__(self):
        self.base_url = "https://www.gumtree.com.au/s-search.html"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
            "Accept-Language": "en-AU,en;q=0.9",
        }

    async def search_listings(self, query: str, location: str = "Queensland", max_results: int = 10) -> List[MarketplaceListing]:
        listings: List[MarketplaceListing] = []
        encoded_query = urllib.parse.quote(query)
        # Search Queensland / Australia
        url = f"https://www.gumtree.com.au/s-search.html?keywords={encoded_query}&locationStr=Queensland"

        try:
            async with httpx.AsyncClient(timeout=10.0, headers=self.headers, follow_redirects=True) as client:
                resp = await client.get(url)
                if resp.status_code == 200:
                    soup = BeautifulSoup(resp.text, "html.parser")
                    cards = soup.find_all("a", class_=re.compile(r"user-ad-row|listing-card|search-result", re.I))

                    for card in cards:
                        if len(listings) >= max_results:
                            break
                        
                        title_elem = card.find(class_=re.compile(r"title|heading", re.I))
                        price_elem = card.find(class_=re.compile(r"price", re.I))
                        loc_elem = card.find(class_=re.compile(r"location", re.I))

                        title = title_elem.get_text(strip=True) if title_elem else card.get_text(strip=True)[:60]
                        href = card.get("href", "")
                        full_url = f"https://www.gumtree.com.au{href}" if href.startswith("/") else href

                        raw_price = price_elem.get_text(strip=True) if price_elem else "$0"
                        price_nums = re.findall(r"\d[\d,]*", raw_price)
                        price_aud = float(price_nums[0].replace(",", "")) if price_nums else 0.0

                        loc = loc_elem.get_text(strip=True) if loc_elem else location

                        listings.append(
                            MarketplaceListing(
                                title=title,
                                source="Gumtree AU",
                                url=full_url or "https://www.gumtree.com.au",
                                price_aud=price_aud,
                                location=loc,
                                condition="used",
                                description=f"Gumtree AU listing: {title} in {loc}",
                            )
                        )
        except Exception as e:
            logger.debug(f"Gumtree search error for '{query}': {e}")

        return listings
