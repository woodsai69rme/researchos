"""
Search Provider Adapters
Base classes and implementations for search providers
"""
import abc
import asyncio
import hashlib
import json
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, AsyncGenerator
from urllib.parse import urlencode, quote_plus

import httpx

from packages.core.config import settings
from packages.core.logging import get_logger
from packages.core.security import free_policy_engine, sanitize_for_llm, validate_url


logger = get_logger("search_providers")


@dataclass
class SearchResult:
    """Standardized search result"""
    url: str
    title: Optional[str] = None
    snippet: Optional[str] = None
    content: Optional[str] = None
    source_type: str = "web"
    relevance_score: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    raw_data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ProviderCapabilities:
    """Provider capabilities and limits"""
    supports_pagination: bool = False
    supports_date_filter: bool = False
    supports_site_filter: bool = False
    supports_language_filter: bool = False
    max_results_per_request: int = 10
    max_query_length: int = 500
    rate_limit_rpm: int = 30
    requires_api_key: bool = True
    is_free: bool = False


class SearchProvider(abc.ABC):
    """Abstract base class for search providers"""
    
    name: str = "base"
    display_name: str = "Base Provider"
    capabilities = ProviderCapabilities()
    
    def __init__(self, api_key: Optional[str] = None, **kwargs):
        self.api_key = api_key
        self.config = kwargs
        self.client = httpx.AsyncClient(timeout=30.0)
        self._request_count = 0
        self._last_request_time = 0.0
    
    @abc.abstractmethod
    async def search(
        self,
        query: str,
        limit: int = 10,
        offset: int = 0,
        **kwargs
    ) -> List[SearchResult]:
        """Execute search query"""
        pass
    
    @abc.abstractmethod
    async def health_check(self) -> bool:
        """Check if provider is healthy"""
        pass
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()
    
    def _rate_limit(self):
        """Simple rate limiting"""
        now = time.time()
        elapsed = now - self._last_request_time
        min_interval = 60.0 / self.capabilities.rate_limit_rpm
        if elapsed < min_interval:
            time.sleep(min_interval - elapsed)
        self._last_request_time = time.time()
        self._request_count += 1
    
    def _generate_content_hash(self, url: str, title: str, snippet: str) -> str:
        """Generate content hash for deduplication"""
        content = f"{url}|{title}|{snippet}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]


class BraveSearchProvider(SearchProvider):
    """Brave Search API provider"""
    
    name = "brave"
    display_name = "Brave Search"
    capabilities = ProviderCapabilities(
        supports_pagination=True,
        supports_date_filter=True,
        max_results_per_request=20,
        rate_limit_rpm=20,
        requires_api_key=True,
        is_free=True,  # Free tier available
    )
    
    BASE_URL = "https://api.search.brave.com/res/v1/web/search"
    
    async def search(
        self,
        query: str,
        limit: int = 10,
        offset: int = 0,
        **kwargs
    ) -> List[SearchResult]:
        if not self.api_key:
            raise ValueError("Brave API key required")
        
        self._rate_limit()
        
        params = {
            "q": query,
            "count": min(limit, self.capabilities.max_results_per_request),
            "offset": offset,
            "safesearch": "moderate",
            "text_decorations": "false",
        }
        
        # Add optional parameters
        if "freshness" in kwargs:
            params["freshness"] = kwargs["freshness"]
        if "country" in kwargs:
            params["country"] = kwargs["country"]
        if "search_lang" in kwargs:
            params["search_lang"] = kwargs["search_lang"]
        
        headers = {
            "Accept": "application/json",
            "X-Subscription-Token": self.api_key,
        }
        
        try:
            response = await self.client.get(self.BASE_URL, params=params, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            results = []
            for item in data.get("web", {}).get("results", []):
                result = SearchResult(
                    url=item.get("url", ""),
                    title=item.get("title"),
                    snippet=item.get("description"),
                    source_type="web",
                    relevance_score=item.get("score"),
                    metadata={
                        "provider": "brave",
                        "age": item.get("age"),
                        "language": item.get("language"),
                        "is_source_local": item.get("is_source_local"),
                        "is_source_news": item.get("is_source_news"),
                    },
                    raw_data=item,
                )
                results.append(result)
            
            logger.info("Brave search completed", query=query[:50], results=len(results))
            return results
            
        except httpx.HTTPStatusError as e:
            logger.error("Brave search failed", error=str(e), status=e.response.status_code)
            raise
        except Exception as e:
            logger.error("Brave search error", error=str(e))
            raise
    
    async def health_check(self) -> bool:
        if not self.api_key:
            return False
        try:
            response = await self.client.get(
                self.BASE_URL,
                params={"q": "test", "count": 1},
                headers={"X-Subscription-Token": self.api_key},
            )
            return response.status_code == 200
        except Exception:
            return False


class TavilySearchProvider(SearchProvider):
    """Tavily AI Search provider"""
    
    name = "tavily"
    display_name = "Tavily AI Search"
    capabilities = ProviderCapabilities(
        supports_pagination=True,
        max_results_per_request=10,
        rate_limit_rpm=20,
        requires_api_key=True,
        is_free=True,  # Free tier available
    )
    
    BASE_URL = "https://api.tavily.com/search"
    
    async def search(
        self,
        query: str,
        limit: int = 10,
        offset: int = 0,
        **kwargs
    ) -> List[SearchResult]:
        if not self.api_key:
            raise ValueError("Tavily API key required")
        
        self._rate_limit()
        
        payload = {
            "api_key": self.api_key,
            "query": query,
            "max_results": min(limit, self.capabilities.max_results_per_request),
            "search_depth": kwargs.get("search_depth", "basic"),
            "include_answer": kwargs.get("include_answer", True),
            "include_raw_content": kwargs.get("include_raw_content", False),
            "include_images": kwargs.get("include_images", False),
        }
        
        if "include_domains" in kwargs:
            payload["include_domains"] = kwargs["include_domains"]
        if "exclude_domains" in kwargs:
            payload["exclude_domains"] = kwargs["exclude_domains"]
        
        try:
            response = await self.client.post(self.BASE_URL, json=payload)
            response.raise_for_status()
            data = response.json()
            
            results = []
            for item in data.get("results", []):
                result = SearchResult(
                    url=item.get("url", ""),
                    title=item.get("title"),
                    snippet=item.get("content"),
                    content=item.get("raw_content"),
                    source_type="web",
                    relevance_score=item.get("score"),
                    metadata={
                        "provider": "tavily",
                        "published_date": item.get("published_date"),
                    },
                    raw_data=item,
                )
                results.append(result)
            
            logger.info("Tavily search completed", query=query[:50], results=len(results))
            return results
            
        except httpx.HTTPStatusError as e:
            logger.error("Tavily search failed", error=str(e), status=e.response.status_code)
            raise
        except Exception as e:
            logger.error("Tavily search error", error=str(e))
            raise
    
    async def health_check(self) -> bool:
        if not self.api_key:
            return False
        try:
            response = await self.client.post(
                self.BASE_URL,
                json={"api_key": self.api_key, "query": "test", "max_results": 1},
            )
            return response.status_code == 200
        except Exception:
            return False


class ExaSearchProvider(SearchProvider):
    """Exa AI Search provider"""
    
    name = "exa"
    display_name = "Exa AI Search"
    capabilities = ProviderCapabilities(
        supports_pagination=True,
        max_results_per_request=10,
        rate_limit_rpm=30,
        requires_api_key=True,
        is_free=True,  # Free tier available
    )
    
    BASE_URL = "https://api.exa.ai/search"
    
    async def search(
        self,
        query: str,
        limit: int = 10,
        offset: int = 0,
        **kwargs
    ) -> List[SearchResult]:
        if not self.api_key:
            raise ValueError("Exa API key required")
        
        self._rate_limit()
        
        payload = {
            "query": query,
            "numResults": min(limit, self.capabilities.max_results_per_request),
            "useAutoprompt": kwargs.get("use_autoprompt", True),
            "type": kwargs.get("type", "neural"),
        }
        
        if "includeDomains" in kwargs:
            payload["includeDomains"] = kwargs["includeDomains"]
        if "excludeDomains" in kwargs:
            payload["excludeDomains"] = kwargs["excludeDomains"]
        if "startCrawlDate" in kwargs:
            payload["startCrawlDate"] = kwargs["startCrawlDate"]
        if "endCrawlDate" in kwargs:
            payload["endCrawlDate"] = kwargs["endCrawlDate"]
        
        headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json",
        }
        
        try:
            response = await self.client.post(self.BASE_URL, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            results = []
            for item in data.get("results", []):
                result = SearchResult(
                    url=item.get("url", ""),
                    title=item.get("title"),
                    snippet=item.get("text"),
                    content=item.get("highlights"),
                    source_type="web",
                    relevance_score=item.get("score"),
                    metadata={
                        "provider": "exa",
                        "author": item.get("author"),
                        "publishedDate": item.get("publishedDate"),
                    },
                    raw_data=item,
                )
                results.append(result)
            
            logger.info("Exa search completed", query=query[:50], results=len(results))
            return results
            
        except httpx.HTTPStatusError as e:
            logger.error("Exa search failed", error=str(e), status=e.response.status_code)
            raise
        except Exception as e:
            logger.error("Exa search error", error=str(e))
            raise
    
    async def health_check(self) -> bool:
        if not self.api_key:
            return False
        try:
            response = await self.client.post(
                self.BASE_URL,
                json={"query": "test", "numResults": 1},
                headers={"x-api-key": self.api_key},
            )
            return response.status_code == 200
        except Exception:
            return False


class SerperSearchProvider(SearchProvider):
    """Serper (Google Search API) provider"""
    
    name = "serper"
    display_name = "Serper Google Search"
    capabilities = ProviderCapabilities(
        supports_pagination=True,
        max_results_per_request=10,
        rate_limit_rpm=30,
        requires_api_key=True,
        is_free=False,  # Paid service
    )
    
    BASE_URL = "https://google.serper.dev/search"
    
    async def search(
        self,
        query: str,
        limit: int = 10,
        offset: int = 0,
        **kwargs
    ) -> List[SearchResult]:
        if not self.api_key:
            raise ValueError("Serper API key required")
        
        self._rate_limit()
        
        payload = {
            "q": query,
            "num": min(limit, self.capabilities.max_results_per_request),
            "start": offset,
        }
        
        if "gl" in kwargs:
            payload["gl"] = kwargs["gl"]
        if "hl" in kwargs:
            payload["hl"] = kwargs["hl"]
        if "type" in kwargs:
            payload["type"] = kwargs["type"]
        
        headers = {
            "X-API-KEY": self.api_key,
            "Content-Type": "application/json",
        }
        
        try:
            response = await self.client.post(self.BASE_URL, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            results = []
            for item in data.get("organic", []):
                result = SearchResult(
                    url=item.get("link", ""),
                    title=item.get("title"),
                    snippet=item.get("snippet"),
                    source_type="web",
                    metadata={
                        "provider": "serper",
                        "position": item.get("position"),
                    },
                    raw_data=item,
                )
                results.append(result)
            
            logger.info("Serper search completed", query=query[:50], results=len(results))
            return results
            
        except httpx.HTTPStatusError as e:
            logger.error("Serper search failed", error=str(e), status=e.response.status_code)
            raise
        except Exception as e:
            logger.error("Serper search error", error=str(e))
            raise
    
    async def health_check(self) -> bool:
        if not self.api_key:
            return False
        try:
            response = await self.client.post(
                self.BASE_URL,
                json={"q": "test", "num": 1},
                headers={"X-API-KEY": self.api_key},
            )
            return response.status_code == 200
        except Exception:
            return False


class DuckDuckGoHTMLProvider(SearchProvider):
    """DuckDuckGo HTML scraping provider (no API key needed)"""
    
    name = "duckduckgo"
    display_name = "DuckDuckGo (HTML)"
    capabilities = ProviderCapabilities(
        supports_pagination=True,
        max_results_per_request=10,
        rate_limit_rpm=10,
        requires_api_key=False,
        is_free=True,
    )
    
    BASE_URL = "https://html.duckduckgo.com/html/"
    
    async def search(
        self,
        query: str,
        limit: int = 10,
        offset: int = 0,
        **kwargs
    ) -> List[SearchResult]:
        self._rate_limit()
        
        params = {
            "q": query,
            "b": offset,
            "kl": kwargs.get("kl", "au-en"),  # Australia English
        }
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        }
        
        try:
            response = await self.client.post(self.BASE_URL, data=params, headers=headers)
            response.raise_for_status()
            
            # Parse HTML
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.text, "html.parser")
            
            results = []
            for result_div in soup.select(".result__body"):
                title_elem = result_div.select_one(".result__title a")
                snippet_elem = result_div.select_one(".result__snippet")
                url_elem = result_div.select_one(".result__url")
                
                if not title_elem:
                    continue
                
                url = title_elem.get("href", "")
                if url and not url.startswith("http"):
                    continue
                
                # Validate URL for SSRF
                valid, _ = validate_url(url)
                if not valid:
                    continue
                
                result = SearchResult(
                    url=url,
                    title=title_elem.get_text(strip=True),
                    snippet=snippet_elem.get_text(strip=True) if snippet_elem else None,
                    source_type="web",
                    metadata={
                        "provider": "duckduckgo",
                        "display_url": url_elem.get_text(strip=True) if url_elem else None,
                    },
                )
                results.append(result)
                
                if len(results) >= limit:
                    break
            
            logger.info("DuckDuckGo search completed", query=query[:50], results=len(results))
            return results
            
        except Exception as e:
            logger.error("DuckDuckGo search error", error=str(e))
            raise
    
    async def health_check(self) -> bool:
        try:
            response = await self.client.post(
                self.BASE_URL,
                data={"q": "test", "b": 0},
                headers={"User-Agent": "Mozilla/5.0"},
            )
            return response.status_code == 200
        except Exception:
            return False


class GoogleHTMLProvider(SearchProvider):
    """Google HTML scraping provider (no API key, but limited)"""
    
    name = "google_html"
    display_name = "Google (HTML)"
    capabilities = ProviderCapabilities(
        supports_pagination=True,
        max_results_per_request=10,
        rate_limit_rpm=5,  # Very conservative
        requires_api_key=False,
        is_free=True,
    )
    
    BASE_URL = "https://www.google.com/search"
    
    async def search(
        self,
        query: str,
        limit: int = 10,
        offset: int = 0,
        **kwargs
    ) -> List[SearchResult]:
        self._rate_limit()
        
        params = {
            "q": query,
            "num": min(limit, self.capabilities.max_results_per_request),
            "start": offset,
            "hl": kwargs.get("hl", "en"),
            "gl": kwargs.get("gl", "au"),
        }
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        }
        
        try:
            response = await self.client.get(self.BASE_URL, params=params, headers=headers)
            response.raise_for_status()
            
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.text, "html.parser")
            
            results = []
            for g in soup.select("div.g"):
                # Skip ads and non-organic results
                if g.select_one(".VwiC3b.yDYNvb"):  # Ad marker
                    continue
                
                link = g.select_one("a")
                if not link:
                    continue
                
                url = link.get("href", "")
                if not url.startswith("http"):
                    continue
                
                # Extract title
                title_elem = g.select_one("h3")
                title = title_elem.get_text(strip=True) if title_elem else None
                
                # Extract snippet
                snippet_elem = g.select_one(".VwiC3b")
                snippet = snippet_elem.get_text(strip=True) if snippet_elem else None
                
                # Validate URL
                valid, _ = validate_url(url)
                if not valid:
                    continue
                
                result = SearchResult(
                    url=url,
                    title=title,
                    snippet=snippet,
                    source_type="web",
                    metadata={"provider": "google_html"},
                )
                results.append(result)
                
                if len(results) >= limit:
                    break
            
            logger.info("Google HTML search completed", query=query[:50], results=len(results))
            return results
            
        except Exception as e:
            logger.error("Google HTML search error", error=str(e))
            raise
    
    async def health_check(self) -> bool:
        try:
            response = await self.client.get(
                self.BASE_URL,
                params={"q": "test"},
                headers={"User-Agent": "Mozilla/5.0"},
            )
            return response.status_code == 200
        except Exception:
            return False


class SearXNGProvider(SearchProvider):
    """SearXNG self-hosted instance provider"""
    
    name = "searxng"
    display_name = "SearXNG"
    capabilities = ProviderCapabilities(
        supports_pagination=True,
        max_results_per_request=20,
        rate_limit_rpm=60,
        requires_api_key=False,
        is_free=True,
    )
    
    def __init__(self, api_key: Optional[str] = None, instance_url: str = None, **kwargs):
        super().__init__(api_key, **kwargs)
        self.instance_url = instance_url or settings.SEARXNG_URL
        if not self.instance_url:
            raise ValueError("SearXNG instance URL required")
    
    async def search(
        self,
        query: str,
        limit: int = 10,
        offset: int = 0,
        **kwargs
    ) -> List[SearchResult]:
        self._rate_limit()
        
        params = {
            "q": query,
            "format": "json",
            "pageno": (offset // limit) + 1,
            "safesearch": kwargs.get("safesearch", "1"),
            "language": kwargs.get("language", "en"),
        }
        
        if "categories" in kwargs:
            params["categories"] = kwargs["categories"]
        if "engines" in kwargs:
            params["engines"] = kwargs["engines"]
        
        try:
            response = await self.client.get(f"{self.instance_url}/search", params=params)
            response.raise_for_status()
            data = response.json()
            
            results = []
            for item in data.get("results", []):
                url = item.get("url", "")
                valid, _ = validate_url(url)
                if not valid:
                    continue
                
                result = SearchResult(
                    url=url,
                    title=item.get("title"),
                    snippet=item.get("content"),
                    source_type="web",
                    relevance_score=item.get("score"),
                    metadata={
                        "provider": "searxng",
                        "engine": item.get("engine"),
                        "category": item.get("category"),
                    },
                    raw_data=item,
                )
                results.append(result)
            
            logger.info("SearXNG search completed", query=query[:50], results=len(results))
            return results
            
        except Exception as e:
            logger.error("SearXNG search error", error=str(e))
            raise
    
    async def health_check(self) -> bool:
        try:
            response = await self.client.get(f"{self.instance_url}/search", params={"q": "test", "format": "json"})
            return response.status_code == 200
        except Exception:
            return False


# ============================================================
# PROVIDER REGISTRY
# ============================================================

class ProviderRegistry:
    """Registry for managing search providers"""
    
    def __init__(self):
        self._providers: Dict[str, SearchProvider] = {}
        self._initialized = False
    
    def register(self, provider: SearchProvider) -> None:
        """Register a provider instance"""
        self._providers[provider.name] = provider
        logger.info("Provider registered", name=provider.name, display_name=provider.display_name)
    
    def get(self, name: str) -> Optional[SearchProvider]:
        """Get provider by name"""
        return self._providers.get(name)
    
    def list(self) -> List[SearchProvider]:
        """List all registered providers"""
        return list(self._providers.values())
    
    def get_enabled_free_providers(self) -> List[SearchProvider]:
        """Get all enabled free providers"""
        return [
            p for p in self._providers.values()
            if p.capabilities.is_free
        ]
    
    def get_all_providers(self) -> List[SearchProvider]:
        """Get all providers (free and paid)"""
        return list(self._providers.values())
    
    async def initialize_from_settings(self) -> None:
        """Initialize providers from settings"""
        if self._initialized:
            return
        
        # Free providers (no API key needed)
        self.register(DuckDuckGoHTMLProvider())
        self.register(GoogleHTMLProvider())
        
        # SearXNG if configured
        if settings.SEARXNG_URL:
            self.register(SearXNGProvider(instance_url=settings.SEARXNG_URL))
        
        # API key providers
        if settings.BRAVE_API_KEY:
            self.register(BraveSearchProvider(api_key=settings.BRAVE_API_KEY))
        
        if settings.TAVILY_API_KEY:
            self.register(TavilySearchProvider(api_key=settings.TAVILY_API_KEY))
        
        if settings.EXA_API_KEY:
            self.register(ExaSearchProvider(api_key=settings.EXA_API_KEY))
        
        if settings.SERPER_API_KEY:
            self.register(SerperSearchProvider(api_key=settings.SERPER_API_KEY))
        
        # SerpAPI would be similar
        
        self._initialized = True
        logger.info("Provider registry initialized", count=len(self._providers))
    
    async def close_all(self) -> None:
        """Close all provider connections"""
        for provider in self._providers.values():
            await provider.close()
        self._providers.clear()
        self._initialized = False


# Global registry instance
provider_registry = ProviderRegistry()