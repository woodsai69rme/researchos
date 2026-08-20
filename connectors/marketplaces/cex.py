"""
ResearchOS CeX (au.webuy.com) Used Electronics & GPU Pricing Connector
"""
import urllib.parse
from typing import List
import httpx
from researchos.packages.core.logging import logger
from researchos.packages.core.schemas import MarketplaceListing


class CeXAUConnector:
    def __init__(self):
        self.api_url = "https://wss2.cex.au.webuy.io/v3/boxes"
        self.headers = {"User-Agent": "ResearchOS-Price-Tracker/1.0 (Windows 11)"}

    async def search_products(self, query: str, max_results: int = 8) -> List[MarketplaceListing]:
        listings: List[MarketplaceListing] = []
        params = {"q": query, "firstRecord": 1, "count": max_results}

        try:
            async with httpx.AsyncClient(timeout=8.0, headers=self.headers) as client:
                resp = await client.get(self.api_url, params=params)
                if resp.status_code == 200:
                    boxes = resp.json().get("response", {}).get("data", {}).get("boxes", [])
                    for box in boxes:
                        name = box.get("boxName", "")
                        price_aud = float(box.get("sellPrice", 0.0))
                        box_id = box.get("boxId", "")
                        category = box.get("categoryFriendlyName", "")
                        out_of_stock = box.get("outOfStock", 0) == 1

                        listings.append(
                            MarketplaceListing(
                                title=name,
                                source="CeX Australia (au.webuy.com)",
                                url=f"https://au.webuy.com/product-detail?id={box_id}",
                                price_aud=price_aud,
                                location="CeX Stores / Online AU",
                                condition="refurbished / 24-month warranty",
                                brand=category,
                                is_available=not out_of_stock,
                                warranty="24 Months CeX Warranty",
                                description=f"CeX Australia refurbished stock: {name}. Price: ${price_aud:.2f} AUD with 24-month store warranty.",
                            )
                        )
        except Exception as e:
            logger.debug(f"CeX AU search exception: {e}")

        return listings
