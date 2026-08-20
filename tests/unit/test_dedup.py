"""
Unit Tests for Source Deduplication & Lineage Tracking
"""
from researchos.packages.core.schemas import SourceDocument
from researchos.packages.evidence.dedup import SourceDeduplicator, normalize_url


def test_url_normalization_removes_tracking_params():
    raw_url = "https://example.com/product?utm_source=twitter&utm_medium=cpc&id=123&gclid=abc"
    normalized = normalize_url(raw_url)
    assert "utm_source" not in normalized
    assert "gclid" not in normalized
    assert "id=123" in normalized


def test_deduplicator_filters_exact_and_syndicated_copies():
    dedup = SourceDeduplicator()

    doc1 = SourceDocument(
        url="https://news.example.com/article-1?ref=1",
        title="Major AI Breakthrough Announced",
        snippet="OpenAI releases new free tier models for all developers worldwide.",
        provider_name="TestA",
    )
    # Exact duplicate with different tracking params
    doc2 = SourceDocument(
        url="https://news.example.com/article-1?utm_medium=social",
        title="Major AI Breakthrough Announced",
        snippet="OpenAI releases new free tier models for all developers worldwide.",
        provider_name="TestB",
    )
    # Syndicated copy on different domain with identical text
    doc3 = SourceDocument(
        url="https://syndicated-news.org/reprint-breakthrough",
        title="Major AI Breakthrough Announced",
        snippet="OpenAI releases new free tier models for all developers worldwide.",
        provider_name="TestC",
    )

    unique_docs, dup_count = dedup.deduplicate([doc1, doc2, doc3])
    assert len(unique_docs) == 2 # doc1 (primary) + doc3 (marked as syndicated copy)
    assert doc3.is_syndicated is True
    assert doc3.parent_source_id == doc1.source_id
    assert dup_count == 2
