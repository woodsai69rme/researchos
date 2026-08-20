"""
Unit Tests for Claims & Contradiction Engine
"""
from researchos.packages.core.schemas import Claim, SourceDocument, ClaimStatus
from researchos.packages.claims.contradiction import ContradictionDetector
from researchos.packages.claims.extractor import ClaimExtractor
from researchos.packages.evidence.graph import EvidenceGraph


def test_contradiction_detected_on_price_divergence():
    detector = ContradictionDetector()

    c1 = Claim(
        claim_text="Pricing for RTX 4090: $1,200 AUD",
        entity="RTX 4090",
        property_type="price",
        supporting_sources=["https://sourceA.com"],
    )
    c2 = Claim(
        claim_text="Pricing for RTX 4090: $2,800 AUD",
        entity="RTX 4090",
        property_type="price",
        supporting_sources=["https://sourceB.com"],
    )

    contradictions = detector.detect_contradictions([c1, c2])
    assert len(contradictions) == 1
    assert contradictions[0].conflict_type == "price"
    assert c1.status == ClaimStatus.DISPUTED
    assert c2.status == ClaimStatus.DISPUTED


def test_claim_extraction_from_document():
    graph = EvidenceGraph()
    extractor = ClaimExtractor(graph)

    doc = SourceDocument(
        url="https://fordperformance.com.au/specs",
        title="Barra 1000hp Package Specs",
        snippet="Our Ford Barra to TH400 conversion package is rated for 1000hp and includes custom SFI bellhousing. Complete package costs $11,500 AUD.",
        provider_name="FordSpecialist",
    )

    claims = extractor.extract_claims_from_documents([doc], entity_hint="Barra TH400")
    assert len(claims) >= 1
    assert any("1000hp" in c.claim_text.lower() or "11,500" in c.claim_text for c in claims)
