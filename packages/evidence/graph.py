"""
ResearchOS Evidence Graph & Lineage Engine
"""
from typing import Dict, List, Optional
from researchos.packages.core.schemas import (
    SourceDocument, EvidenceNode, Claim, CredibilityTier
)


class EvidenceGraph:
    def __init__(self):
        self.sources: Dict[str, SourceDocument] = {}
        self.evidence_nodes: Dict[str, EvidenceNode] = {}
        self.claims: Dict[str, Claim] = {}
        self.source_to_evidence: Dict[str, List[str]] = {} # source_id -> list of evidence_ids
        self.claim_to_evidence: Dict[str, List[str]] = {}  # claim_id -> list of evidence_ids

    def add_source(self, source: SourceDocument):
        self.sources[source.source_id] = source
        if source.source_id not in self.source_to_evidence:
            self.source_to_evidence[source.source_id] = []

    def create_evidence_node(self, source_id: str, excerpt: str, confidence: float = 0.85) -> Optional[EvidenceNode]:
        source = self.sources.get(source_id)
        if not source:
            return None

        node = EvidenceNode(
            source_id=source_id,
            source_url=source.url,
            source_title=source.title,
            excerpt=excerpt,
            credibility=source.credibility,
            confidence=confidence,
        )
        self.evidence_nodes[node.evidence_id] = node
        self.source_to_evidence[source_id].append(node.evidence_id)
        return node

    def link_claim(self, claim: Claim, supporting_evidence_ids: List[str], contradicting_evidence_ids: List[str] = None):
        self.claims[claim.claim_id] = claim
        for eid in supporting_evidence_ids:
            if eid in self.evidence_nodes:
                claim.supporting_evidence.append(self.evidence_nodes[eid])
                if self.evidence_nodes[eid].source_url not in claim.supporting_sources:
                    claim.supporting_sources.append(self.evidence_nodes[eid].source_url)
        
        if contradicting_evidence_ids:
            for eid in contradicting_evidence_ids:
                if eid in self.evidence_nodes:
                    claim.contradicting_evidence.append(self.evidence_nodes[eid])

    def calculate_claim_independence(self, claim_id: str) -> int:
        """Counts truly independent primary/secondary source nodes supporting a claim."""
        claim = self.claims.get(claim_id)
        if not claim:
            return 0
        independent_roots = set()
        for node in claim.supporting_evidence:
            src = self.sources.get(node.source_id)
            if src:
                # If syndicated, map to parent source root
                root_id = src.parent_source_id or src.source_id
                independent_roots.add(root_id)
        return len(independent_roots)
