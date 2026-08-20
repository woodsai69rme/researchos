"""
ResearchOS Parallel Multi-Provider Search Swarm Coordinator
"""
import asyncio
from typing import List
from researchos.packages.core.logging import logger
from researchos.packages.core.schemas import ResearchPlan, SourceDocument, MarketplaceListing, BusinessListing
from researchos.packages.core.events import event_bus, ResearchEvent, ResearchEventType
from researchos.packages.providers.registry import provider_registry
from researchos.connectors.code.github import GitHubConnector
from researchos.connectors.social.reddit import RedditConnector
from researchos.connectors.social.youtube import YouTubeConnector
from researchos.connectors.marketplaces.gumtree import GumtreeAUConnector
from researchos.connectors.marketplaces.ebay import EbayAUConnector
from researchos.connectors.marketplaces.cashies import CashConvertersAUConnector
from researchos.connectors.marketplaces.cex import CeXAUConnector
from researchos.packages.business.workshop_finder import WorkshopFinder
from researchos.packages.evidence.dedup import SourceDeduplicator


class SearchSwarm:
    def __init__(self):
        self.github = GitHubConnector()
        self.reddit = RedditConnector()
        self.youtube = YouTubeConnector()
        self.gumtree = GumtreeAUConnector()
        self.ebay = EbayAUConnector()
        self.cashies = CashConvertersAUConnector()
        self.cex = CeXAUConnector()
        self.workshop_finder = WorkshopFinder()
        self.deduplicator = SourceDeduplicator()

    async def execute_swarm(self, plan: ResearchPlan) -> dict:
        """
        Executes parallel searches across all available search engines, social feeds,
        code repositories, marketplaces, and workshop directories.
        """
        all_sources: List[SourceDocument] = []
        all_listings: List[MarketplaceListing] = []
        all_businesses: List[BusinessListing] = []

        await event_bus.emit(
            ResearchEvent(
                run_id=plan.plan_id,
                event_type=ResearchEventType.PROVIDER_QUERYING,
                step_title="Launching Search Swarm",
                message=f"Dispatching parallel queries across web, code, marketplace, community, and directories for: '{plan.original_query}'",
            )
        )

        # 1. Search Web Engines
        search_providers = await provider_registry.get_active_search_providers(free_only=plan.free_only)
        tasks = []

        for p in search_providers:
            for q in plan.search_queries[:2]:
                tasks.append(self._safe_search(p, q))

        # 2. Search GitHub & Community (Reddit, YouTube)
        tasks.append(self._safe_github(plan.original_query))
        tasks.append(self._safe_reddit(plan.original_query))
        tasks.append(self._safe_youtube(plan.original_query))

        # 3. Search Marketplaces
        tasks.append(self._safe_marketplace(plan.original_query))

        # 4. Search Workshops / Businesses
        tasks.append(self._safe_workshops(plan.original_query, plan.geographic_scope))

        # Run all swarm queries concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)

        for res in results:
            if isinstance(res, list):
                for item in res:
                    if isinstance(item, SourceDocument):
                        all_sources.append(item)
                    elif isinstance(item, MarketplaceListing):
                        all_listings.append(item)
                    elif isinstance(item, BusinessListing):
                        all_businesses.append(item)

        # Deduplicate sources and track lineages
        unique_sources, dup_count = self.deduplicator.deduplicate(all_sources)

        await event_bus.emit(
            ResearchEvent(
                run_id=plan.plan_id,
                event_type=ResearchEventType.DEDUPLICATION_DONE,
                step_title="Deduplication Complete",
                message=f"Discovered {len(all_sources)} total hits; synthesized into {len(unique_sources)} unique sources ({dup_count} duplicates/syndicated links resolved).",
                payload={"unique_count": len(unique_sources), "listings_count": len(all_listings), "workshops_count": len(all_businesses)},
            )
        )

        return {
            "sources": unique_sources,
            "listings": all_listings,
            "businesses": all_businesses,
        }

    async def _safe_search(self, provider, query: str) -> List[SourceDocument]:
        try:
            return await provider.search(query, max_results=6)
        except Exception as e:
            logger.debug(f"Provider {provider.name} search error: {e}")
            return []

    async def _safe_github(self, query: str) -> List[SourceDocument]:
        try:
            return await self.github.search_repositories(query, max_results=5)
        except Exception as e:
            return []

    async def _safe_reddit(self, query: str) -> List[SourceDocument]:
        try:
            return await self.reddit.search_discussions(query, max_results=6)
        except Exception as e:
            return []

    async def _safe_youtube(self, query: str) -> List[SourceDocument]:
        try:
            return await self.youtube.search_videos(query, max_results=4)
        except Exception as e:
            return []

    async def _safe_marketplace(self, query: str) -> List[MarketplaceListing]:
        listings = []
        try:
            gt = await self.gumtree.search_listings(query, max_results=5)
            listings.extend(gt)
        except Exception:
            pass
        try:
            eb = await self.ebay.search_listings(query, max_results=5)
            listings.extend(eb)
        except Exception:
            pass
        try:
            cc = await self.cashies.search_listings(query, max_results=4)
            listings.extend(cc)
        except Exception:
            pass
        try:
            cx = await self.cex.search_products(query, max_results=4)
            listings.extend(cx)
        except Exception:
            pass
        return listings

    async def _safe_workshops(self, query: str, location: str) -> List[BusinessListing]:
        try:
            return await self.workshop_finder.find_workshops(query, location=location, max_results=6)
        except Exception:
            return []
