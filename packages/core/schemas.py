"""
ResearchOS Core Pydantic Data Models and Schemas
"""
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, HttpUrl
import uuid


class ProviderType(str, Enum):
    SEARCH = "search"
    AI_MODEL = "ai_model"
    MARKETPLACE = "marketplace"
    CODE = "code"
    SOCIAL = "social"
    BUSINESS = "business"
    SCRAPER = "scraper"


class ProviderStatus(str, Enum):
    ONLINE = "ONLINE"
    DEGRADED = "DEGRADED"
    RATE_LIMITED = "RATE_LIMITED"
    QUOTA_EXHAUSTED = "QUOTA_EXHAUSTED"
    AUTH_ERROR = "AUTH_ERROR"
    UNAVAILABLE = "UNAVAILABLE"
    DISABLED = "DISABLED"
    UNKNOWN = "UNKNOWN"


class CredibilityTier(str, Enum):
    PRIMARY = "PRIMARY"          # Government, official docs, primary repo, manufacturer specs
    SECONDARY = "SECONDARY"      # Reputable tech news, peer-reviewed, verified benchmarks
    COMMUNITY = "COMMUNITY"      # Reddit, YouTube, forums, user discussions
    LOWER = "LOWER"              # Unverified blogs, aggregated deal sites, anonymous posts


class ClaimStatus(str, Enum):
    CONFIRMED = "CONFIRMED"
    STRONGLY_SUPPORTED = "STRONGLY_SUPPORTED"
    PROBABLE = "PROBABLE"
    DISPUTED = "DISPUTED"
    UNVERIFIED = "UNVERIFIED"
    CONTRADICTED = "CONTRADICTED"
    STALE = "STALE"


class PromotionStatus(str, Enum):
    ACTIVE = "ACTIVE"
    EXPIRING = "EXPIRING"
    EXPIRED = "EXPIRED"
    UNVERIFIED = "UNVERIFIED"
    COMMUNITY_REPORTED = "COMMUNITY_REPORTED"
    DISPUTED = "DISPUTED"


class ResearchPlan(BaseModel):
    plan_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    original_query: str
    normalized_query: str
    intent: str
    domain_category: str = "general"
    subcategories: List[str] = Field(default_factory=list)
    entities: List[str] = Field(default_factory=list)
    synonyms: List[str] = Field(default_factory=list)
    spelling_variants: List[str] = Field(default_factory=list)
    model_variants: List[str] = Field(default_factory=list)
    part_number_variants: List[str] = Field(default_factory=list)
    geographic_scope: str = "Australia"
    source_classes: List[str] = Field(default_factory=list)
    search_queries: List[str] = Field(default_factory=list)
    required_evidence: List[str] = Field(default_factory=list)
    exclusions: List[str] = Field(default_factory=list)
    budget: float = 0.0
    currency: str = "AUD"
    free_only: bool = True
    operating_mode: str = "FREE_ONLY"
    monitoring_interval: Optional[int] = None
    priority: str = "normal"
    urgency: str = "medium"
    stop_conditions: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class SourceDocument(BaseModel):
    source_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    url: str
    canonical_url: Optional[str] = None
    title: str
    snippet: str
    raw_content: Optional[str] = None
    provider_name: str
    credibility: CredibilityTier = CredibilityTier.COMMUNITY
    published_date: Optional[str] = None
    author_or_domain: str = ""
    is_syndicated: bool = False
    parent_source_id: Optional[str] = None
    fetched_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class EvidenceNode(BaseModel):
    evidence_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    source_id: str
    source_url: str
    source_title: str
    excerpt: str
    credibility: CredibilityTier
    confidence: float = Field(ge=0.0, le=1.0, default=0.8)
    extracted_at: datetime = Field(default_factory=datetime.utcnow)


class Claim(BaseModel):
    claim_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    claim_text: str
    entity: str
    property_type: str = "general" # price, compatibility, free_tier, feature, spec
    supporting_evidence: List[EvidenceNode] = Field(default_factory=list)
    supporting_sources: List[str] = Field(default_factory=list)
    contradicting_evidence: List[EvidenceNode] = Field(default_factory=list)
    confidence: float = 0.8
    status: ClaimStatus = ClaimStatus.UNVERIFIED
    last_verified: datetime = Field(default_factory=datetime.utcnow)


class Contradiction(BaseModel):
    contradiction_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    entity: str
    conflict_type: str # price, specification, compatibility, free_tier, quota, availability
    claim_a: str
    source_a: str
    claim_b: str
    source_b: str
    explanation: str
    detected_at: datetime = Field(default_factory=datetime.utcnow)


class MarketplaceListing(BaseModel):
    listing_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    source: str # Gumtree, eBay, Cash Converters, CeX, Carsales, FB Marketplace
    url: str
    price_aud: float
    original_price: Optional[float] = None
    original_currency: str = "AUD"
    seller: str = "Unknown"
    seller_type: str = "private" # private, dealer, business, retailer
    location: str = "Australia"
    distance_km: Optional[float] = None
    condition: str = "used" # new, used, refurbished, parts
    brand: str = ""
    model: str = ""
    variant: str = ""
    part_number: Optional[str] = None
    description: str = ""
    listing_date: Optional[str] = None
    shipping_available: bool = False
    shipping_cost_aud: float = 0.0
    warranty: Optional[str] = None
    is_available: bool = True
    photos: List[str] = Field(default_factory=list)
    compatibility_notes: str = ""
    completeness: str = "complete"
    deal_score: float = 0.0 # 0 to 100
    deal_score_reasons: List[str] = Field(default_factory=list)
    confidence: float = 0.85
    last_checked: datetime = Field(default_factory=datetime.utcnow)


class BusinessListing(BaseModel):
    business_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    address: str
    suburb: str = ""
    state: str = "QLD"
    postcode: str = ""
    country: str = "AU"
    distance_km: Optional[float] = None
    website: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    services: List[str] = Field(default_factory=list)
    specializations: List[str] = Field(default_factory=list)
    evidence: List[str] = Field(default_factory=list)
    reviews_summary: str = ""
    rating: Optional[float] = None
    review_count: int = 0
    forum_mentions_count: int = 0
    confidence: float = 0.85


class Promotion(BaseModel):
    promo_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    provider: str
    plan_name: str
    offer_summary: str
    amount_value: Optional[float] = None
    currency: str = "AUD"
    country: str = "AU"
    start_date: Optional[str] = None
    expiry_date: Optional[str] = None
    card_required: bool = False
    auto_renew: bool = False
    commercial_use: bool = True
    restrictions: List[str] = Field(default_factory=list)
    official_source_url: Optional[str] = None
    community_source_urls: List[str] = Field(default_factory=list)
    last_verified: datetime = Field(default_factory=datetime.utcnow)
    confidence: float = 0.9
    status: PromotionStatus = PromotionStatus.ACTIVE


class ModelSpec(BaseModel):
    model_id: str
    provider: str
    model_name: str
    version: str = "1.0"
    context_window: int = 128000
    max_output_tokens: int = 4096
    modalities: List[str] = Field(default_factory=lambda: ["text"])
    vision_supported: bool = False
    audio_supported: bool = False
    tool_use_supported: bool = True
    reasoning_supported: bool = False
    coding_score_swe_bench: Optional[float] = None
    agent_score: Optional[float] = None
    is_open_weights: bool = False
    is_local_capable: bool = False
    recommended_vram_gb: Optional[float] = None
    is_free_tier_available: bool = True
    free_limits_description: str = "Free on OpenRouter / Local Ollama"
    price_per_m_input_usd: float = 0.0
    price_per_m_output_usd: float = 0.0
    effective_cost_aud: float = 0.0
    latency_seconds_approx: float = 2.0
    last_verified: datetime = Field(default_factory=datetime.utcnow)


class VideoProviderCost(BaseModel):
    provider_name: str
    model_name: str
    free_generations_daily: int = 0
    free_generations_monthly: int = 0
    generation_length_seconds: int = 5
    max_resolution: str = "720p"
    has_watermark: bool = False
    queue_priority: str = "standard"
    commercial_use_allowed: bool = False
    subscription_cost_monthly_aud: float = 0.0
    credit_cost_per_clip_aud: float = 0.0
    cost_per_minute_aud: float = 0.0
    estimated_music_video_clips: int = 40
    estimated_total_music_video_cost_aud: float = 0.0
    last_verified: datetime = Field(default_factory=datetime.utcnow)


class ReviewSentimentSummary(BaseModel):
    positive_percentage: float = 0.0
    negative_percentage: float = 0.0
    mixed_percentage: float = 0.0
    neutral_percentage: float = 0.0
    top_praise: List[str] = Field(default_factory=list)
    top_complaints: List[str] = Field(default_factory=list)
    most_common_bugs: List[str] = Field(default_factory=list)
    most_common_limitations: List[str] = Field(default_factory=list)
    top_use_cases: List[str] = Field(default_factory=list)
    community_confidence_score: float = 0.8


class FinalResearchReport(BaseModel):
    report_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    original_query: str
    operating_mode: str
    actual_spend_aud: float = 0.0
    paid_providers_executed: int = 0
    free_providers_used: List[str] = Field(default_factory=list)
    local_models_used: List[str] = Field(default_factory=list)
    executive_summary: str
    bottom_line: str
    best_options: List[Dict[str, Any]] = Field(default_factory=list)
    free_options: List[Dict[str, Any]] = Field(default_factory=list)
    cheap_options: List[Dict[str, Any]] = Field(default_factory=list)
    best_value: Optional[Dict[str, Any]] = None
    similar_and_alternatives: List[Dict[str, Any]] = Field(default_factory=list)
    what_you_missed: List[str] = Field(default_factory=list)
    marketplace_results: List[MarketplaceListing] = Field(default_factory=list)
    business_results: List[BusinessListing] = Field(default_factory=list)
    promotions: List[Promotion] = Field(default_factory=list)
    ai_models: List[ModelSpec] = Field(default_factory=list)
    video_costs: List[VideoProviderCost] = Field(default_factory=list)
    community_reviews: Optional[ReviewSentimentSummary] = None
    claims: List[Claim] = Field(default_factory=list)
    contradictions: List[Contradiction] = Field(default_factory=list)
    sources: List[SourceDocument] = Field(default_factory=list)
    evidence_nodes: List[EvidenceNode] = Field(default_factory=list)
    risks_and_limitations: List[str] = Field(default_factory=list)
    unknown_information: List[str] = Field(default_factory=list)
    confidence_score: float = 0.85
    created_at: datetime = Field(default_factory=datetime.utcnow)
    next_check_time: Optional[datetime] = None


class Watchlist(BaseModel):
    watchlist_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    target_query: str
    category: str # ai_models, coding, video, marketplace, automotive, electronics, promotions
    check_interval_hours: int = 12
    last_checked: Optional[datetime] = None
    next_check: Optional[datetime] = None
    is_active: bool = True
    last_snapshot_hash: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Alert(BaseModel):
    alert_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    watchlist_id: Optional[str] = None
    title: str
    message: str
    category: str
    significance: str # LOW, MEDIUM, HIGH, CRITICAL
    old_value: Optional[str] = None
    new_value: Optional[str] = None
    source_url: Optional[str] = None
    confidence: float = 0.9
    created_at: datetime = Field(default_factory=datetime.utcnow)
    read: bool = False
