"""
Unit Tests for Marketplace Deal Scorer
"""
from researchos.packages.core.schemas import MarketplaceListing
from researchos.packages.marketplace.deal_scorer import DealScorer


def test_deal_scorer_awards_high_score_for_discounted_items():
    scorer = DealScorer()

    deal_good = MarketplaceListing(
        title="ASUS TUF RTX 4090 24GB",
        source="CeX Australia (au.webuy.com)",
        url="https://au.webuy.com/example",
        price_aud=1800.0,
        location="Brisbane, QLD",
        warranty="24 Months CeX Warranty",
        condition="refurbished / 24-month warranty",
    )

    deal_overpriced = MarketplaceListing(
        title="Used RTX 4090",
        source="Gumtree AU",
        url="https://gumtree.com.au/example",
        price_aud=3400.0,
        location="Sydney, NSW",
    )

    scored_list = scorer.score_all([deal_good, deal_overpriced])
    assert scored_list[0].title == "ASUS TUF RTX 4090 24GB"
    assert scored_list[0].deal_score > scored_list[1].deal_score
    assert scored_list[0].deal_score >= 80.0
