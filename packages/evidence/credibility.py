"""
ResearchOS Source Credibility Evaluation & Hierarchy Engine
"""
import urllib.parse
from researchos.packages.core.schemas import CredibilityTier

PRIMARY_DOMAINS = {
    "github.com", "gov.au", "edu.au", "openai.com", "anthropic.com", "google.com",
    "meta.com", "mistral.ai", "deepseek.com", "openrouter.ai", "ford.com.au", "ford.com",
    "nvidia.com", "huggingface.co", "microsoft.com", "aws.amazon.com", "apple.com"
}

SECONDARY_DOMAINS = {
    "arxiv.org", "theverge.com", "techcrunch.com", "arstechnica.com", "tomshardware.com",
    "anandtech.com", "motortrend.com", "whichcar.com.au", "carsales.com.au", "drive.com.au",
    "caradvice.com.au", "reuters.com", "bloomberg.com", "abc.net.au"
}

COMMUNITY_DOMAINS = {
    "reddit.com", "youtube.com", "whirlpool.net.au", "fordforums.com.au", "boostcruising.com",
    "gumtree.com.au", "ebay.com.au", "facebook.com", "ozbargain.com.au", "news.ycombinator.com"
}


def evaluate_credibility(url: str, title: str = "") -> CredibilityTier:
    """Classifies a URL into a strict credibility tier based on primary domain taxonomy."""
    try:
        domain = urllib.parse.urlparse(url).netloc.lower()
        if domain.startswith("www."):
            domain = domain[4:]

        for p in PRIMARY_DOMAINS:
            if domain == p or domain.endswith("." + p):
                return CredibilityTier.PRIMARY

        for s in SECONDARY_DOMAINS:
            if domain == s or domain.endswith("." + s):
                return CredibilityTier.SECONDARY

        for c in COMMUNITY_DOMAINS:
            if domain == c or domain.endswith("." + c):
                return CredibilityTier.COMMUNITY

    except Exception:
        pass

    return CredibilityTier.SECONDARY
