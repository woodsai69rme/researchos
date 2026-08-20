"""
ResearchOS eBay Australia Marketplace Connector
"""
import re
import urllib.parse
from typing import List
import httpx
from bs4 import BeautifulSoup
from researchos.packages.core.logging import logger
from researchos.packages.core.schemas import MarketplaceListing


class EbayAUConnector:
    def __init__(self):
        self.base_url = "https://www.ebay.com.au/sch/i.html"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
            "Accept-Language": "en-AU,en;q=0.9",
        }

    async def search_listings(self, query: str, max_results: int = 10) -> List[MarketplaceListing]:
        listings: List[MarketplaceListing] = []
        encoded = urllib.parse.quote(query)
        # &LH_PrefLoc=1 filters for items located in Australia
        url = f"{self.base_url}?_nkw={encoded}&LH_PrefLoc=1&_sop=12"

        try:
            async with httpx.AsyncClient(timeout=10.0, headers=self.headers, follow_redirects=True) as client:
                resp = await client.get(url)
                if resp.status_code == 200:
                    soup = BeautifulSoup(resp.text, "html.parser")
                    items = soup.find_all("li", class_=re.compile(r"s-item", re.I))

                    for item in items:
                        if len(listings) >= max_results:
                            break
                        
                        title_el = item.find("div", class_="s-item__title") or item.find("h3")
                        price_el = item.find("span", class_="s-item__price")
                        link_el = item.find("a", class_="s-item__link")
                        loc_el = item.find("span", class_="s-item__location")

                        if not title_el or not price_el or not link_el:
                            continue

                        title = title_el.get_text(strip=True)
                        if "Shop on eBay" in title:
                            continue

                        raw_price = price_el.get_text(strip=True)
                        price_nums = re.findall(r"\d[\d,]*\.?\d*", raw_price)
                        price_aud = float(price_nums[0].replace(",", "")) if price_nums else 0.0

                        link = link_el.get("href", "").split("?")[0]
                        location = loc_el.get_text(strip=True) if loc_el else "Australia"

                        listings.append(
                            MarketplaceListing(
                                title=title,
                                source="eBay AU",
                                url=link,
                                price_aud=price_aud,
                                location=location,
                                condition="used" if "pre-owned" in title.lower() or "used" in title.lower() else "new",
                                description=f"eBay Australia item: {title} located in {location}",
                            )
                        )
        except Exception as e:
            logger.debug(f"eBay AU search error: {e}")

        return listings
