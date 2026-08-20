"""
ResearchOS Factual Claim Extraction & Classification Engine
"""
import re
from typing import List, Tuple
from researchos.packages.core.schemas import (
    Claim, ClaimStatus, SourceDocument, CredibilityTier
)
from researchos.packages.evidence.graph import EvidenceGraph


class ClaimExtractor:
    def __init__(self, evidence_graph: EvidenceGraph):
        self.graph = evidence_graph

    def extract_claims_from_documents(self, documents: List[SourceDocument], entity_hint: str = "") -> List[Claim]:
        claims: List[Claim] = []

        # Patterns for extracting price, free-tier, compatibility, and horsepower/spec claims
        price_patterns = [
            re.compile(r"(\$\s*[\d,]+(?:\.\d+)?\s*(?:AUD|USD|free|monthly|per\s+month)?)", re.I),
            re.compile(r"(free\s+(?:tier|trial|credits?|for\s+developers))", re.I),
        ]
        spec_patterns = [
            re.compile(r"(\d{3,4}\s*(?:hp|rwhp|rwkw|kw|horsepower))", re.I),
            re.compile(r"(fits|compatible\s+with|bolts\s+to|conversion\s+kit|bellhousing\s+for)\s+([A-Za-z0-9\s\-]+)", re.I),
            re.compile(r"(\d+k\s+context|context\s+window\s+of\s+\d+k)", re.I),
        ]

        for doc in documents:
            self.graph.add_source(doc)
            text = f"{doc.title}. {doc.snippet}"
            
            # Extract spec & compatibility claims
            for p in spec_patterns:
                matches = p.findall(text)
                for m in matches:
                    claim_str = f"{entity_hint or doc.author_or_domain}: {m if isinstance(m, str) else ' '.join(m)}"
                    ev = self.graph.create_evidence_node(doc.source_id, excerpt=text[:250])
                    if ev:
                        cl = Claim(
                            claim_text=claim_str,
                            entity=entity_hint or doc.author_or_domain,
                            property_type="specification",
                            status=ClaimStatus.CONFIRMED if doc.credibility == CredibilityTier.PRIMARY else ClaimStatus.PROBABLE,
                            confidence=0.9 if doc.credibility == CredibilityTier.PRIMARY else 0.75,
                        )
                        self.graph.link_claim(cl, [ev.evidence_id])
                        claims.append(cl)

            # Extract pricing claims
            for p in price_patterns:
                matches = p.findall(text)
                for m in matches:
                    claim_str = f"Pricing for {entity_hint or doc.title}: {m}"
                    ev = self.graph.create_evidence_node(doc.source_id, excerpt=text[:250])
                    if ev:
                        cl = Claim(
                            claim_text=claim_str,
                            entity=entity_hint or doc.author_or_domain,
                            property_type="price",
                            status=ClaimStatus.STRONGLY_SUPPORTED if doc.credibility in (CredibilityTier.PRIMARY, CredibilityTier.SECONDARY) else ClaimStatus.PROBABLE,
                            confidence=0.85,
                        )
                        self.graph.link_claim(cl, [ev.evidence_id])
                        claims.append(cl)

        return claims
