"""
ResearchOS Qdrant Vector Database Module
Async Qdrant client for embeddings and semantic search
"""
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional, List, Dict, Any
from uuid import UUID

from qdrant_client import AsyncQdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue,
    SearchRequest,
    ScoredPoint,
)

from .config import settings


_qdrant_client: Optional[AsyncQdrantClient] = None


def init_qdrant() -> None:
    """Initialize Qdrant client"""
    global _qdrant_client

    if _qdrant_client is not None:
        return

    _qdrant_client = AsyncQdrantClient(
        url=settings.QDRANT_URL,
        timeout=30,
    )


async def close_qdrant() -> None:
    """Close Qdrant client"""
    global _qdrant_client
    if _qdrant_client is not None:
        await _qdrant_client.close()
        _qdrant_client = None


async def get_qdrant() -> AsyncGenerator[AsyncQdrantClient, None]:
    """Get Qdrant client for dependency injection"""
    if _qdrant_client is None:
        init_qdrant()

    yield _qdrant_client


@asynccontextmanager
async def get_qdrant_context() -> AsyncGenerator[AsyncQdrantClient, None]:
    """Get Qdrant client as context manager"""
    if _qdrant_client is None:
        init_qdrant()

    yield _qdrant_client


# ============================================================
# COLLECTION MANAGEMENT
# ============================================================

COLLECTIONS = {
    "documents": 768,  # sentence-transformers all-MiniLM-L6-v2
    "claims": 768,
    "products": 768,
    "entities": 768,
    "reviews": 768,
    "research_history": 768,
    "sources": 768,
}


async def init_collections(client: AsyncQdrantClient) -> None:
    """Initialize all required collections"""
    for collection_name, vector_size in COLLECTIONS.items():
        exists = await client.collection_exists(collection_name)
        if not exists:
            await client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
            )


async def delete_collection(client: AsyncQdrantClient, collection_name: str) -> None:
    """Delete a collection"""
    await client.delete_collection(collection_name)


# ============================================================
# HIGH-LEVEL VECTOR OPERATIONS
# ============================================================

class QdrantManager:
    """High-level Qdrant operations for ResearchOS"""

    def __init__(self, client: AsyncQdrantClient):
        self.client = client

    # ---- Documents ----
    async def upsert_document(
        self,
        doc_id: UUID,
        embedding: List[float],
        payload: Dict[str, Any],
    ) -> None:
        """Upsert document embedding"""
        point = PointStruct(
            id=str(doc_id),
            vector=embedding,
            payload=payload,
        )
        await self.client.upsert(collection_name="documents", points=[point])

    async def search_documents(
        self,
        query_embedding: List[float],
        limit: int = 10,
        score_threshold: float = 0.7,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[ScoredPoint]:
        """Search similar documents"""
        query_filter = None
        if filters:
            conditions = []
            for key, value in filters.items():
                conditions.append(FieldCondition(key=key, match=MatchValue(value=value)))
            query_filter = Filter(must=conditions)

        results = await self.client.search(
            collection_name="documents",
            query_vector=query_embedding,
            limit=limit,
            score_threshold=score_threshold,
            query_filter=query_filter,
        )
        return results

    async def delete_document(self, doc_id: UUID) -> None:
        """Delete document by ID"""
        await self.client.delete(
            collection_name="documents",
            points_selector=[str(doc_id)],
        )

    # ---- Claims ----
    async def upsert_claim(
        self,
        claim_id: UUID,
        embedding: List[float],
        payload: Dict[str, Any],
    ) -> None:
        """Upsert claim embedding"""
        point = PointStruct(
            id=str(claim_id),
            vector=embedding,
            payload=payload,
        )
        await self.client.upsert(collection_name="claims", points=[point])

    async def search_claims(
        self,
        query_embedding: List[float],
        limit: int = 10,
        score_threshold: float = 0.7,
    ) -> List[ScoredPoint]:
        """Search similar claims"""
        results = await self.client.search(
            collection_name="claims",
            query_vector=query_embedding,
            limit=limit,
            score_threshold=score_threshold,
        )
        return results

    # ---- Products ----
    async def upsert_product(
        self,
        product_id: UUID,
        embedding: List[float],
        payload: Dict[str, Any],
    ) -> None:
        """Upsert product embedding"""
        point = PointStruct(
            id=str(product_id),
            vector=embedding,
            payload=payload,
        )
        await self.client.upsert(collection_name="products", points=[point])

    async def search_products(
        self,
        query_embedding: List[float],
        limit: int = 10,
        score_threshold: float = 0.7,
        category: Optional[str] = None,
    ) -> List[ScoredPoint]:
        """Search similar products"""
        query_filter = None
        if category:
            query_filter = Filter(
                must=[FieldCondition(key="category", match=MatchValue(value=category))]
            )

        results = await self.client.search(
            collection_name="products",
            query_vector=query_embedding,
            limit=limit,
            score_threshold=score_threshold,
            query_filter=query_filter,
        )
        return results

    # ---- Entities ----
    async def upsert_entity(
        self,
        entity_id: UUID,
        embedding: List[float],
        payload: Dict[str, Any],
    ) -> None:
        """Upsert entity embedding"""
        point = PointStruct(
            id=str(entity_id),
            vector=embedding,
            payload=payload,
        )
        await self.client.upsert(collection_name="entities", points=[point])

    async def search_entities(
        self,
        query_embedding: List[float],
        limit: int = 10,
        score_threshold: float = 0.7,
        entity_type: Optional[str] = None,
    ) -> List[ScoredPoint]:
        """Search similar entities"""
        query_filter = None
        if entity_type:
            query_filter = Filter(
                must=[FieldCondition(key="entity_type", match=MatchValue(value=entity_type))]
            )

        results = await self.client.search(
            collection_name="entities",
            query_vector=query_embedding,
            limit=limit,
            score_threshold=score_threshold,
            query_filter=query_filter,
        )
        return results

    # ---- Reviews ----
    async def upsert_review(
        self,
        review_id: UUID,
        embedding: List[float],
        payload: Dict[str, Any],
    ) -> None:
        """Upsert review embedding"""
        point = PointStruct(
            id=str(review_id),
            vector=embedding,
            payload=payload,
        )
        await self.client.upsert(collection_name="reviews", points=[point])

    async def search_reviews(
        self,
        query_embedding: List[float],
        limit: int = 10,
        score_threshold: float = 0.7,
        sentiment: Optional[str] = None,
    ) -> List[ScoredPoint]:
        """Search similar reviews"""
        query_filter = None
        if sentiment:
            query_filter = Filter(
                must=[FieldCondition(key="sentiment", match=MatchValue(value=sentiment))]
            )

        results = await self.client.search(
            collection_name="reviews",
            query_vector=query_embedding,
            limit=limit,
            score_threshold=score_threshold,
            query_filter=query_filter,
        )
        return results

    # ---- Research History ----
    async def upsert_research_history(
        self,
        run_id: UUID,
        embedding: List[float],
        payload: Dict[str, Any],
    ) -> None:
        """Upsert research run embedding for similarity search"""
        point = PointStruct(
            id=str(run_id),
            vector=embedding,
            payload=payload,
        )
        await self.client.upsert(collection_name="research_history", points=[point])

    async def search_research_history(
        self,
        query_embedding: List[float],
        limit: int = 5,
        score_threshold: float = 0.7,
    ) -> List[ScoredPoint]:
        """Find similar past research runs"""
        results = await self.client.search(
            collection_name="research_history",
            query_vector=query_embedding,
            limit=limit,
            score_threshold=score_threshold,
        )
        return results

    # ---- Sources ----
    async def upsert_source(
        self,
        source_id: UUID,
        embedding: List[float],
        payload: Dict[str, Any],
    ) -> None:
        """Upsert source embedding"""
        point = PointStruct(
            id=str(source_id),
            vector=embedding,
            payload=payload,
        )
        await self.client.upsert(collection_name="sources", points=[point])

    async def search_sources(
        self,
        query_embedding: List[float],
        limit: int = 10,
        score_threshold: float = 0.7,
        tier: Optional[str] = None,
    ) -> List[ScoredPoint]:
        """Search similar sources"""
        query_filter = None
        if tier:
            query_filter = Filter(
                must=[FieldCondition(key="tier", match=MatchValue(value=tier))]
            )

        results = await self.client.search(
            collection_name="sources",
            query_vector=query_embedding,
            limit=limit,
            score_threshold=score_threshold,
            query_filter=query_filter,
        )
        return results

    # ---- Batch Operations ----
    async def batch_upsert(
        self,
        collection: str,
        points: List[PointStruct],
    ) -> None:
        """Batch upsert points"""
        await self.client.upsert(collection_name=collection, points=points)

    async def batch_delete(self, collection: str, ids: List[UUID]) -> None:
        """Batch delete points"""
        await self.client.delete(
            collection_name=collection,
            points_selector=[str(id) for id in ids],
        )

    # ---- Collection Stats ----
    async def get_collection_info(self, collection: str) -> Dict[str, Any]:
        """Get collection statistics"""
        info = await self.client.get_collection(collection)
        return {
            "name": collection,
            "vectors_count": info.vectors_count,
            "indexed_vectors_count": info.indexed_vectors_count,
            "points_count": info.points_count,
            "segments_count": info.segments_count,
            "status": info.status,
        }


async def get_qdrant_manager() -> QdrantManager:
    """Get Qdrant manager instance"""
    if _qdrant_client is None:
        init_qdrant()
    return QdrantManager(_qdrant_client)