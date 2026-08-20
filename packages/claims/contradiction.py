"""
ResearchOS Contradiction Detection Engine
"""
import re
from typing import List
from researchos.packages.core.schemas import Claim, Contradiction, ClaimStatus


class ContradictionDetector:
    def detect_contradictions(self, claims: List[Claim]) -> List[Contradiction]:
        contradictions: List[Contradiction] = []
        
        # Group claims by entity and property type
        grouped = {}
        for c in claims:
            key = (c.entity.lower(), c.property_type)
            if key not in grouped:
                grouped[key] = []
            grouped[key].append(c)

        for (entity, prop), group in grouped.items():
            if len(group) < 2:
                continue

            for i in range(len(group)):
                for j in range(i + 1, len(group)):
                    c1 = group[i]
                    c2 = group[j]

                    # Price contradiction detection
                    if prop == "price":
                        p1_match = re.findall(r"\$\s*([\d,]+)", c1.claim_text)
                        p2_match = re.findall(r"\$\s*([\d,]+)", c2.claim_text)
                        if p1_match and p2_match:
                            v1 = float(p1_match[0].replace(",", ""))
                            v2 = float(p2_match[0].replace(",", ""))
                            # Conflict if prices differ by more than 20%
                            if v1 > 0 and v2 > 0 and abs(v1 - v2) / max(v1, v2) > 0.20:
                                contradictions.append(
                                    Contradiction(
                                        entity=entity,
                                        conflict_type="price",
                                        claim_a=c1.claim_text,
                                        source_a=c1.supporting_sources[0] if c1.supporting_sources else "Source A",
                                        claim_b=c2.claim_text,
                                        source_b=c2.supporting_sources[0] if c2.supporting_sources else "Source B",
                                        explanation=f"Price discrepancy detected between ${v1:,.2f} and ${v2:,.2f}. Likely due to different product revisions, condition, or regional pricing.",
                                    )
                                )
                                c1.status = ClaimStatus.DISPUTED
                                c2.status = ClaimStatus.DISPUTED

                    # Free tier vs Paid contradiction
                    if "free" in c1.claim_text.lower() and ("paid" in c2.claim_text.lower() or "$" in c2.claim_text):
                        contradictions.append(
                            Contradiction(
                                entity=entity,
                                conflict_type="free_tier",
                                claim_a=c1.claim_text,
                                source_a=c1.supporting_sources[0] if c1.supporting_sources else "Source A",
                                claim_b=c2.claim_text,
                                source_b=c2.supporting_sources[0] if c2.supporting_sources else "Source B",
                                explanation="Free tier status contradiction: One source claims free tier/credits while another indicates paid subscription required. Official pricing page is prioritized.",
                            )
                        )

        return contradictions
