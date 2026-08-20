"""
ResearchOS Cash Converters Australia Second-Hand Deals Connector
"""
import re
import urllib.parse
from typing import List
import httpx
from bs4 import BeautifulSoup
from researchos.packages.core.logging import logger
from researchos.packages.core.schemas import MarketplaceListing


class CashConvertersAUConnector:
    def __init__(self):
        self.base_url = "https://www.cashconverters.com.au/search"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept-Language": "en-AU,en;q=0.9",
        }

    async def search_listings(self, query: str, state: str = "QLD", max_results: int = 8) -> List[MarketplaceListing]:
        listings: List[MarketplaceListing] = []
        encoded = urllib.parse.quote(query)
        url = f"https://www.cashconverters.com.au/search?query={encoded}"

        try:
            async with httpx.AsyncClient(timeout=10.0, headers=self.headers, follow_redirects=True) as client:
                resp = await client.get(url)
                if resp.status_code == 200:
                    soup = BeautifulSoup(resp.text, "html.parser")
                    products = soup.find_all(class_=re.compile(r"product-card|search-result__item", re.I))

                    for item in products:
                        if len(listings) >= max_results:
                            break
                        
                        title_el = item.find(class_=re.compile(r"title|name", re.I))
                        price_el = item.find(class_=re.compile(r"price", re.I))
                        store_el = item.find(class_=re.compile(r"store|location", re.I))
                        link_el = item.find("a")

                        if not title_el or not price_el:
                            continue

                        title = title_el.get_text(strip=True)
                        raw_price = price_el.get_text(strip=True)
                        price_nums = re.findall(r"\d[\d,]*", raw_price)
                        price_aud = float(price_nums[0].replace(",", "")) if price_nums else 0.0

                        store = store_el.get_text(strip=True) if store_el else "Cash Converters QLD Store"
                        href = link_el.get("href", "") if link_el else ""
                        full_url = f"https://www.cashconverters.com.au{href}" if href.startswith("/") else href

                        listings.append(
                            MarketplaceListing(
                                title=title,
                                source="Cash Converters AU",
                                url=full_url or "https://www.cashconverters.com.au",
                                price_aud=price_aud,
                                location=store,
                                condition="second-hand / inspected",
                                description=f"Cash Converters item in {store}: {title}",
                            )
                        )
        except Exception as e:
            logger.debug(f"Cash Converters search error: {e}")

        return listings
