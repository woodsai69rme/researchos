# ResearchOS Marketplace Search & Deal Scoring Guide

## Supported Australian Marketplaces
- **Gumtree Australia:** Private and trade listings across Queensland and nationally.
- **eBay Australia:** Local stock (`LH_PrefLoc=1`) with buyer protection.
- **Cash Converters Australia:** Second-hand inspected electronics and tools in local store branches.
- **CeX Australia (au.webuy.com):** Refurbished PC components and GPUs with standard **24-month store warranty**.
- **Carsales / CarsGuide:** Public automotive classifieds.

## Deal Scoring Algorithm (0 - 100)
Every listing is scored using a multi-factor formula:
1. **Price Discount vs Market Median (up to 50 pts):** Items >30% below market average receive maximum score bonuses.
2. **Warranty & Condition (up to 20 pts):** Verified warranties (e.g. CeX 24 months) boost score significantly.
3. **Merchant Trust & Protection (up to 15 pts):** Commercial buyer protection and inspected store stock.
4. **Location Proximity (up to 15 pts):** Local Queensland / Brisbane listings prioritized for in-person inspection.
