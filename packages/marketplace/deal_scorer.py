"""
ResearchOS Marketplace Deal Score Algorithm
"""
from typing import List, Tuple
from researchos.packages.core.schemas import MarketplaceListing


class DealScorer:
    def calculate_deal_score(self, listing: MarketplaceListing, market_median_price: float) -> Tuple[float, List[str]]:
        """
        Calculates deal score (0 - 100) based on:
        - Price discount vs market median (up to 50 pts)
        - Condition & Warranty (up to 20 pts)
        - Seller Confidence & Platform Trust (up to 15 pts)
        - Location proximity & Completeness (up to 15 pts)
        """
        reasons = []
        score = 50.0 # base score

        # 1. Price vs Market Median
        if market_median_price > 0 and listing.price_aud > 0:
            price_ratio = listing.price_aud / market_median_price
            if price_ratio < 0.70: # >30% below market
                score += 30.0
                reasons.append(f"Exceptional price: ${listing.price_aud:,.2f} is {(1.0 - price_ratio)*100:.0f}% below market median of ${market_median_price:,.2f}.")
            elif price_ratio < 0.90: # 10-30% below market
                score += 15.0
                reasons.append(f"Competitive price: ${listing.price_aud:,.2f} is {(1.0 - price_ratio)*100:.0f}% below market median.")
            elif price_ratio > 1.25:
                score -= 20.0
                reasons.append(f"Priced above market average (${listing.price_aud:,.2f} vs ${market_median_price:,.2f}).")

        # 2. Condition & Warranty
        if listing.warranty:
            score += 10.0
            reasons.append(f"Includes warranty: {listing.warranty}")
        if listing.condition in ("new", "refurbished / 24-month warranty"):
            score += 10.0
            reasons.append(f"Verified condition: {listing.condition}")

        # 3. Seller trust & Platform
        if listing.source in ("CeX Australia (au.webuy.com)", "Cash Converters AU"):
            score += 5.0
            reasons.append("Commercial store protection / verified merchant")

        # 4. Location relevance (Queensland / Brisbane preference)
        if any(loc in listing.location.lower() for loc in ["brisbane", "queensland", "qld", "gold coast", "sunshine coast"]):
            score += 5.0
            reasons.append(f"Local Queensland listing in {listing.location}")

        final_score = max(0.0, min(100.0, round(score, 1)))
        listing.deal_score = final_score
        listing.deal_score_reasons = reasons
        return final_score, reasons

    def score_all(self, listings: List[MarketplaceListing]) -> List[MarketplaceListing]:
        if not listings:
            return []
        
        valid_prices = [l.price_aud for l in listings if l.price_aud > 0]
        if valid_prices:
            valid_prices.sort()
            median_price = valid_prices[len(valid_prices) // 2]
        else:
            median_price = 0.0

        for l in listings:
            self.calculate_deal_score(l, median_price)

        # Sort highest deal score first
        listings.sort(key=lambda x: x.deal_score, reverse=True)
        return listings
