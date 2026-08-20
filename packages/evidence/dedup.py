"""
ResearchOS Source Deduplication & Syndication Lineage Tracker
"""
import hashlib
import re
import urllib.parse
from typing import Dict, List, Tuple
from researchos.packages.core.schemas import SourceDocument


def normalize_url(url: str) -> str:
    """Strips tracking params (utm_*, gclid, ref, etc.) to get canonical URL."""
    try:
        parsed = urllib.parse.urlparse(url)
        params = urllib.parse.parse_qsl(parsed.query)
        cleaned_params = [
            (k, v) for k, v in params if not (
                k.startswith("utm_") or k in ("gclid", "fbclid", "ref", "source", "ref_src", "t", "s")
            )
        ]
        new_query = urllib.parse.urlencode(cleaned_params)
        return urllib.parse.urlunparse((parsed.scheme, parsed.netloc.lower(), parsed.path.rstrip("/"), "", new_query, ""))
    except Exception:
        return url.split("?")[0].rstrip("/")


def compute_content_fingerprint(text: str) -> str:
    """Computes a MinHash/SimHash-style fingerprint of normalized text for copy detection."""
    clean = re.sub(r"[^a-zA-Z0-9\s]", "", text.lower())
    words = clean.split()
    if not words:
        return ""
    # Take first 50 content words
    sample = " ".join(words[:50])
    return hashlib.md5(sample.encode("utf-8")).hexdigest()


class SourceDeduplicator:
    def __init__(self):
        self.seen_urls: Dict[str, str] = {} # canonical_url -> source_id
        self.seen_fingerprints: Dict[str, str] = {} # fingerprint -> primary_source_id

    def deduplicate(self, documents: List[SourceDocument]) -> Tuple[List[SourceDocument], int]:
        """
        Deduplicates a list of documents:
        - Filters out exact duplicate canonical URLs
        - Identifies syndicated/copied press releases and links them to the primary source
        """
        unique_docs: List[SourceDocument] = []
        duplicates_count = 0

        for doc in documents:
            canonical = normalize_url(doc.url)
            doc.canonical_url = canonical

            if canonical in self.seen_urls:
                duplicates_count += 1
                continue

            fingerprint = compute_content_fingerprint(doc.snippet or doc.title)
            if fingerprint and fingerprint in self.seen_fingerprints:
                # Mark as syndicated copy rather than independent confirmation
                doc.is_syndicated = True
                doc.parent_source_id = self.seen_fingerprints[fingerprint]
                duplicates_count += 1
                unique_docs.append(doc)
                self.seen_urls[canonical] = doc.source_id
            else:
                self.seen_urls[canonical] = doc.source_id
                if fingerprint:
                    self.seen_fingerprints[fingerprint] = doc.source_id
                unique_docs.append(doc)

        return unique_docs, duplicates_count
