"""
ResearchOS Core Database Models
SQLAlchemy 2.0 async models with full type safety
"""
import enum
import uuid
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from decimal import Decimal

from sqlalchemy import (
    String,
    Text,
    Integer,
    Float,
    Boolean,
    DateTime,
    Enum as SQLEnum,
    ForeignKey,
    Index,
    UniqueConstraint,
    JSON,
    ARRAY,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship, DeclarativeBase
from sqlalchemy.sql import func


class Base(DeclarativeBase):
    pass


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


class UUIDMixin:
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )


# ============================================================
# ENUMS
# ============================================================

class FreePolicyMode(str, enum.Enum):
    FREE_ONLY = "FREE_ONLY"
    FREE_FIRST = "FREE_FIRST"
    CHEAP = "CHEAP"
    FULL = "FULL"


class ProviderStatus(str, enum.Enum):
    ONLINE = "ONLINE"
    DEGRADED = "DEGRADED"
    RATE_LIMITED = "RATE_LIMITED"
    QUOTA_EXHAUSTED = "QUOTA_EXHAUSTED"
    AUTH_ERROR = "AUTH_ERROR"
    UNAVAILABLE = "UNAVAILABLE"
    DISABLED = "DISABLED"
    UNKNOWN = "UNKNOWN"


class ProviderType(str, enum.Enum):
    SEARCH = "SEARCH"
    AI = "AI"
    MARKETPLACE = "MARKETPLACE"
    BUSINESS = "BUSINESS"
    ACADEMIC = "ACADEMIC"
    GOVERNMENT = "GOVERNMENT"
    SOCIAL = "SOCIAL"
    CODE = "CODE"


class ResearchDepth(str, enum.Enum):
    QUICK = "QUICK"
    NORMAL = "NORMAL"
    DEEP = "DEEP"
    MAXIMUM = "MAXIMUM"


class ResearchStatus(str, enum.Enum):
    PLANNING = "PLANNING"
    SEARCHING = "SEARCHING"
    EXTRACTING = "EXTRACTING"
    VERIFYING = "VERIFYING"
    SYNTHESIZING = "SYNTHESIZING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class SourceTier(str, enum.Enum):
    PRIMARY = "PRIMARY"
    SECONDARY = "SECONDARY"
    COMMUNITY = "COMMUNITY"
    LOWER_CONFIDENCE = "LOWER_CONFIDENCE"


class ClaimStatus(str, enum.Enum):
    CONFIRMED = "CONFIRMED"
    STRONGLY_SUPPORTED = "STRONGLY_SUPPORTED"
    PROBABLE = "PROBABLE"
    DISPUTED = "DISPUTED"
    UNVERIFIED = "UNVERIFIED"
    CONTRADICTED = "CONTRADICTED"
    STALE = "STALE"


class ListingCondition(str, enum.Enum):
    NEW = "NEW"
    USED = "USED"
    REFURBISHED = "REFURBISHED"
    OPEN_BOX = "OPEN_BOX"
    PARTS = "PARTS"
    UNKNOWN = "UNKNOWN"


class SellerType(str, enum.Enum):
    PRIVATE = "PRIVATE"
    BUSINESS = "BUSINESS"
    DEALERSHIP = "DEALERSHIP"
    AUCTION = "AUCTION"
    PAWN_SHOP = "PAWN_SHOP"
    RECYCLER = "RECYCLER"
    UNKNOWN = "UNKNOWN"


class PromotionStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    EXPIRING = "EXPIRING"
    EXPIRED = "EXPIRED"
    UNVERIFIED = "UNVERIFIED"
    COMMUNITY_REPORTED = "COMMUNITY_REPORTED"
    DISPUTED = "DISPUTED"


class ReviewSentiment(str, enum.Enum):
    POSITIVE = "POSITIVE"
    NEGATIVE = "NEGATIVE"
    MIXED = "MIXED"
    NEUTRAL = "NEUTRAL"


class AlertChannel(str, enum.Enum):
    BROWSER = "BROWSER"
    EMAIL = "EMAIL"
    DESKTOP = "DESKTOP"
    WEBHOOK = "WEBHOOK"
    TELEGRAM = "TELEGRAM"
    DISCORD = "DISCORD"


class WatchlistType(str, enum.Enum):
    AI_MODELS = "AI_MODELS"
    AI_TOOLS = "AI_TOOLS"
    AI_CODING = "AI_CODING"
    AI_VIDEO = "AI_VIDEO"
    PRICES = "PRICES"
    FREE_TIERS = "FREE_TIERS"
    PROMOTIONS = "PROMOTIONS"
    MARKETPLACES = "MARKETPLACES"
    PRODUCTS = "PRODUCTS"
    BUSINESSES = "BUSINESSES"
    WORKSHOPS = "WORKSHOPS"
    GITHUB_REPOS = "GITHUB_REPOS"
    FORUMS = "FORUMS"
    NEWS = "NEWS"
    COMPANIES = "COMPANIES"


# ============================================================
# USERS & PROJECTS
# ============================================================

class User(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    username: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    free_only_mode: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    max_spend_aud: Mapped[Decimal] = mapped_column(default=0, nullable=False)
    default_currency: Mapped[str] = mapped_column(String(3), default="AUD", nullable=False)
    default_country: Mapped[str] = mapped_column(String(2), default="AU", nullable=False)
    default_timezone: Mapped[str] = mapped_column(String(50), default="Australia/Brisbane", nullable=False)

    # Relationships
    projects: Mapped[List["Project"]] = relationship(back_populates="owner", lazy="selectin")
    watchlists: Mapped[List["Watchlist"]] = relationship(back_populates="owner", lazy="selectin")
    alerts: Mapped[List["Alert"]] = relationship(back_populates="user", lazy="selectin")


class Project(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "projects"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    owner_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    free_only_mode: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    max_spend_aud: Mapped[Decimal] = mapped_column(default=0, nullable=False)
    default_currency: Mapped[str] = mapped_column(String(3), default="AUD", nullable=False)
    default_country: Mapped[str] = mapped_column(String(2), default="AU", nullable=False)
    default_location: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Relationships
    owner: Mapped["User"] = relationship(back_populates="projects", lazy="selectin")
    research_runs: Mapped[List["ResearchRun"]] = relationship(back_populates="project", lazy="selectin")


# ============================================================
# RESEARCH
# ============================================================

class ResearchRun(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "research_runs"

    project_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("projects.id"), nullable=False, index=True)
    query: Mapped[str] = mapped_column(Text, nullable=False)
    normalized_query: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    intent: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    entities: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB, nullable=True)
    categories: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String), nullable=True)
    subcategories: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String), nullable=True)
    synonyms: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String), nullable=True)
    geographic_scope: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    source_classes: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String), nullable=True)
    budget_aud: Mapped[Decimal] = mapped_column(default=0, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="AUD", nullable=False)
    free_only: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    research_depth: Mapped[ResearchDepth] = mapped_column(
        SQLEnum(ResearchDepth), default=ResearchDepth.NORMAL, nullable=False
    )
    monitoring_interval_hours: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    status: Mapped[ResearchStatus] = mapped_column(
        SQLEnum(ResearchStatus), default=ResearchStatus.PLANNING, nullable=False
    )
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    total_cost_aud: Mapped[Decimal] = mapped_column(default=0, nullable=False)
    providers_used: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String), nullable=True)
    free_quotas_consumed: Mapped[Optional[Dict[str, int]]] = mapped_column(JSONB, nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    project: Mapped["Project"] = relationship(back_populates="research_runs", lazy="selectin")
    plan: Mapped[Optional["ResearchPlan"]] = relationship(back_populates="run", lazy="selectin", uselist=False)
    searches: Mapped[List["Search"]] = relationship(back_populates="run", lazy="selectin")
    report: Mapped[Optional["Report"]] = relationship(back_populates="run", lazy="selectin", uselist=False)


class ResearchPlan(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "research_plans"

    run_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("research_runs.id"), unique=True, nullable=False, index=True)
    search_queries: Mapped[List[str]] = mapped_column(ARRAY(String), nullable=False)
    required_evidence: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String), nullable=True)
    exclusions: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String), nullable=True)
    priority: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    urgency: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    stop_conditions: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB, nullable=True)
    estimated_cost_aud: Mapped[Decimal] = mapped_column(default=0, nullable=False)

    # Relationships
    run: Mapped["ResearchRun"] = relationship(back_populates="plan", lazy="selectin")


class Search(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "searches"

    run_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("research_runs.id"), nullable=False, index=True)
    provider: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    query: Mapped[str] = mapped_column(Text, nullable=False)
    query_variant: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    parameters: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="pending", nullable=False)
    results_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    cost_aud: Mapped[Decimal] = mapped_column(default=0, nullable=False)
    latency_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    run: Mapped["ResearchRun"] = relationship(back_populates="searches", lazy="selectin")
    results: Mapped[List["SearchResult"]] = relationship(back_populates="search", lazy="selectin")


class SearchResult(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "search_results"

    search_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("searches.id"), nullable=False, index=True)
    url: Mapped[str] = mapped_column(Text, nullable=False)
    title: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    snippet: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    source_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    source_tier: Mapped[Optional[SourceTier]] = mapped_column(SQLEnum(SourceTier), nullable=True)
    item_metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column("metadata", JSONB, nullable=True)
    relevance_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    content_hash: Mapped[Optional[str]] = mapped_column(String(64), nullable=True, index=True)
    is_duplicate: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    duplicate_of_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("search_results.id"), nullable=True)

    # Relationships
    search: Mapped["Search"] = relationship(back_populates="results", lazy="selectin")
    documents: Mapped[List["Document"]] = relationship(back_populates="source_result", lazy="selectin")


class Document(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "documents"

    source_result_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("search_results.id"), nullable=False, index=True)
    url: Mapped[str] = mapped_column(Text, nullable=False)
    title: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    content_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    language: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    word_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    extracted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    extraction_method: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    item_metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column("metadata", JSONB, nullable=True)
    embedding: Mapped[Optional[List[float]]] = mapped_column(ARRAY(Float), nullable=True)

    # Relationships
    source_result: Mapped["SearchResult"] = relationship(back_populates="documents", lazy="selectin")
    entities: Mapped[List["Entity"]] = relationship(back_populates="document", lazy="selectin")
    claims: Mapped[List["Claim"]] = relationship(back_populates="document", lazy="selectin")
    reviews: Mapped[List["Review"]] = relationship(back_populates="document", lazy="selectin")


# ============================================================
# PROVIDERS
# ============================================================

class Provider(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "providers"

    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    display_name: Mapped[str] = mapped_column(String(255), nullable=False)
    provider_type: Mapped[ProviderType] = mapped_column(SQLEnum(ProviderType), nullable=False, index=True)
    base_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    api_version: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    status: Mapped[ProviderStatus] = mapped_column(
        SQLEnum(ProviderStatus), default=ProviderStatus.UNKNOWN, nullable=False
    )
    is_free: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    free_quota: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    free_quota_reset_period: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    pricing_info: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB, nullable=True)
    billing_required: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    capabilities: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String), nullable=True)
    rate_limit_rpm: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    rate_limit_tpm: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    last_verified: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    last_success: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    last_failure: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    health_check_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    config_schema: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB, nullable=True)
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    priority: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Relationships
    usage_logs: Mapped[List["ProviderUsage"]] = relationship(back_populates="provider", lazy="selectin")


class ProviderUsage(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "provider_usage"

    provider_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("providers.id"), nullable=False, index=True)
    run_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("research_runs.id"), nullable=True, index=True)
    operation: Mapped[str] = mapped_column(String(100), nullable=False)
    request_count: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    tokens_used: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    cost_aud: Mapped[Decimal] = mapped_column(default=0, nullable=False)
    success: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    latency_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Relationships
    provider: Mapped["Provider"] = relationship(back_populates="usage_logs", lazy="selectin")


# ============================================================
# SOURCES & EVIDENCE
# ============================================================

class Source(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "sources"

    url: Mapped[str] = mapped_column(Text, nullable=False, index=True)
    domain: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    title: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    tier: Mapped[SourceTier] = mapped_column(SQLEnum(SourceTier), nullable=False)
    source_type: Mapped[str] = mapped_column(String(100), nullable=False)
    credibility_score: Mapped[float] = mapped_column(Float, default=0.5, nullable=False)
    last_crawled: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    robots_txt_allows: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    content_hash: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    item_metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column("metadata", JSONB, nullable=True)

    # Relationships
    lineage_from: Mapped[List["SourceLineage"]] = relationship(
        foreign_keys="SourceLineage.copied_from_id", back_populates="copied_from", lazy="selectin"
    )
    lineage_to: Mapped[List["SourceLineage"]] = relationship(
        foreign_keys="SourceLineage.source_id", back_populates="source", lazy="selectin"
    )
    evidence: Mapped[List["Evidence"]] = relationship(back_populates="source", lazy="selectin")


class SourceLineage(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "source_lineage"

    source_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("sources.id"), nullable=False, index=True)
    copied_from_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("sources.id"), nullable=False, index=True)
    similarity_score: Mapped[float] = mapped_column(Float, nullable=False)
    detection_method: Mapped[str] = mapped_column(String(100), nullable=False)

    # Relationships
    source: Mapped["Source"] = relationship(foreign_keys=[source_id], back_populates="lineage_to", lazy="selectin")
    copied_from: Mapped["Source"] = relationship(foreign_keys=[copied_from_id], back_populates="lineage_from", lazy="selectin")

    __table_args__ = (UniqueConstraint("source_id", "copied_from_id", name="uq_source_lineage"),)


class Evidence(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "evidence"

    source_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("sources.id"), nullable=False, index=True)
    document_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("documents.id"), nullable=True, index=True)
    claim_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("claims.id"), nullable=True, index=True)
    entity_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("entities.id"), nullable=True, index=True)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    context: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    confidence: Mapped[float] = mapped_column(Float, default=0.5, nullable=False)
    extraction_method: Mapped[str] = mapped_column(String(100), nullable=False)
    supports_claim: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    source: Mapped["Source"] = relationship(back_populates="evidence", lazy="selectin")
    document: Mapped[Optional["Document"]] = relationship(back_populates="evidence", lazy="selectin")
    claim: Mapped[Optional["Claim"]] = relationship(back_populates="evidence", lazy="selectin")
    entity: Mapped[Optional["Entity"]] = relationship(back_populates="evidence", lazy="selectin")


# ============================================================
# ENTITIES & CLAIMS
# ============================================================

class Entity(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "entities"

    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    normalized_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    entity_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    category: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    subcategory: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    variants: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String), nullable=True)
    attributes: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB, nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    confidence: Mapped[float] = mapped_column(Float, default=0.5, nullable=False)

    # Relationships
    document: Mapped[Optional["Document"]] = relationship(back_populates="entities", lazy="selectin")
    evidence: Mapped[List["Evidence"]] = relationship(back_populates="entity", lazy="selectin")
    products: Mapped[List["Product"]] = relationship(back_populates="entity", lazy="selectin")
    claims: Mapped[List["Claim"]] = relationship(back_populates="entity", lazy="selectin")


class Claim(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "claims"

    claim_text: Mapped[str] = mapped_column(Text, nullable=False)
    entity_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("entities.id"), nullable=True, index=True)
    claim_type: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[ClaimStatus] = mapped_column(SQLEnum(ClaimStatus), default=ClaimStatus.UNVERIFIED, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, default=0.5, nullable=False)
    supporting_sources_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    contradicting_sources_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_verified: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    verification_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    item_metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column("metadata", JSONB, nullable=True)

    # Relationships
    entity: Mapped[Optional["Entity"]] = relationship(back_populates="claims", lazy="selectin")
    document: Mapped[Optional["Document"]] = relationship(back_populates="claims", lazy="selectin")
    evidence: Mapped[List["Evidence"]] = relationship(back_populates="claim", lazy="selectin")
    contradictions: Mapped[List["Contradiction"]] = relationship(back_populates="claim", lazy="selectin")


class Contradiction(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "contradictions"

    claim_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("claims.id"), nullable=False, index=True)
    contradicting_claim_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("claims.id"), nullable=False, index=True)
    conflict_type: Mapped[str] = mapped_column(String(100), nullable=False)
    reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    resolution: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    confidence: Mapped[float] = mapped_column(Float, default=0.5, nullable=False)

    # Relationships
    claim: Mapped["Claim"] = relationship(foreign_keys=[claim_id], back_populates="contradictions", lazy="selectin")
    contradicting_claim: Mapped["Claim"] = relationship(foreign_keys=[contradicting_claim_id], lazy="selectin")


# ============================================================
# PRODUCTS & MARKETPLACE
# ============================================================

class Product(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "products"

    entity_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("entities.id"), nullable=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    normalized_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    brand: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    model: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    variant: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    part_number: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    category: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    subcategory: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    specifications: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB, nullable=True)
    compatibility: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB, nullable=True)
    release_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    discontinued_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    official_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    image_urls: Mapped[Optional[List[str]]] = mapped_column(ARRAY(Text), nullable=True)

    # Relationships
    entity: Mapped[Optional["Entity"]] = relationship(back_populates="products", lazy="selectin")
    listings: Mapped[List["Listing"]] = relationship(back_populates="product", lazy="selectin")
    pricing_snapshots: Mapped[List["PricingSnapshot"]] = relationship(back_populates="product", lazy="selectin")


class Listing(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "listings"

    product_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("products.id"), nullable=True, index=True)
    source: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    source_url: Mapped[str] = mapped_column(Text, nullable=False)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    price: Mapped[Optional[Decimal]] = mapped_column(nullable=True)
    currency: Mapped[str] = mapped_column(String(3), default="AUD", nullable=False)
    seller: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    seller_type: Mapped[Optional[SellerType]] = mapped_column(SQLEnum(SellerType), nullable=True)
    location: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    distance_km: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    condition: Mapped[Optional[ListingCondition]] = mapped_column(SQLEnum(ListingCondition), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    listing_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    updated_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    shipping_info: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    warranty_info: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    availability: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    photos: Mapped[Optional[List[str]]] = mapped_column(ARRAY(Text), nullable=True)
    compatibility_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    completeness_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, default=0.5, nullable=False)
    deal_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    deal_score_breakdown: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    product: Mapped[Optional["Product"]] = relationship(back_populates="listings", lazy="selectin")


class PricingSnapshot(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "pricing_snapshots"

    product_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("products.id"), nullable=False, index=True)
    source: Mapped[str] = mapped_column(String(100), nullable=False)
    price: Mapped[Decimal] = mapped_column(nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="AUD", nullable=False)
    price_type: Mapped[str] = mapped_column(String(50), nullable=False)  # retail, sale, used, etc.
    condition: Mapped[Optional[ListingCondition]] = mapped_column(SQLEnum(ListingCondition), nullable=True)
    volume: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    item_metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column("metadata", JSONB, nullable=True)

    # Relationships
    product: Mapped["Product"] = relationship(back_populates="pricing_snapshots", lazy="selectin")


# ============================================================
# BUSINESSES
# ============================================================

class Business(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "businesses"

    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    normalized_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    suburb: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    state: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    postcode: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    country: Mapped[str] = mapped_column(String(2), default="AU", nullable=False)
    latitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    longitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    website: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    services: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String), nullable=True)
    specializations: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String), nullable=True)
    business_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    evidence_sources: Mapped[Optional[List[str]]] = mapped_column(ARRAY(Text), nullable=True)
    forum_mentions: Mapped[Optional[List[str]]] = mapped_column(ARRAY(Text), nullable=True)
    review_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    confidence: Mapped[float] = mapped_column(Float, default=0.5, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Relationships
    reviews: Mapped[List["BusinessReview"]] = relationship(back_populates="business", lazy="selectin")


class BusinessReview(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "business_reviews"

    business_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("businesses.id"), nullable=False, index=True)
    source: Mapped[str] = mapped_column(String(100), nullable=False)
    source_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    rating: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    sentiment: Mapped[ReviewSentiment] = mapped_column(SQLEnum(ReviewSentiment), nullable=False)
    text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    author: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    review_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    helpful_votes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Relationships
    business: Mapped["Business"] = relationship(back_populates="reviews", lazy="selectin")


# ============================================================
# REVIEWS
# ============================================================

class Review(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "reviews"

    document_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("documents.id"), nullable=True, index=True)
    entity_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("entities.id"), nullable=True, index=True)
    source: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    source_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    title: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    sentiment: Mapped[ReviewSentiment] = mapped_column(SQLEnum(ReviewSentiment), nullable=False)
    rating: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    categories: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String), nullable=True)
    pros: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String), nullable=True)
    cons: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String), nullable=True)
    use_cases: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String), nullable=True)
    limitations: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String), nullable=True)
    bugs_reported: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String), nullable=True)
    author: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    author_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    review_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    helpful_votes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    confidence: Mapped[float] = mapped_column(Float, default=0.5, nullable=False)
    is_duplicate: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    duplicate_group_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("reviews.id"), nullable=True)

    # Relationships
    document: Mapped[Optional["Document"]] = relationship(back_populates="reviews", lazy="selectin")


# ============================================================
# PROMOTIONS
# ============================================================

class Promotion(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "promotions"

    provider: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    plan: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    offer: Mapped[str] = mapped_column(Text, nullable=False)
    amount: Mapped[Optional[Decimal]] = mapped_column(nullable=True)
    currency: Mapped[str] = mapped_column(String(3), default="AUD", nullable=False)
    country: Mapped[str] = mapped_column(String(2), default="AU", nullable=False)
    free_limit: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    start_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    expiry_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True, index=True)
    card_required: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    auto_renew: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    commercial_use: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    restrictions: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String), nullable=True)
    official_source_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    community_sources: Mapped[Optional[List[str]]] = mapped_column(ARRAY(Text), nullable=True)
    last_verified: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    confidence: Mapped[float] = mapped_column(Float, default=0.5, nullable=False)
    status: Mapped[PromotionStatus] = mapped_column(
        SQLEnum(PromotionStatus), default=PromotionStatus.UNVERIFIED, nullable=False
    )
    item_metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column("metadata", JSONB, nullable=True)


# ============================================================
# AI MODELS
# ============================================================

class AIModel(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "ai_models"

    provider: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    model_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    model_name: Mapped[str] = mapped_column(String(255), nullable=False)
    version: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    context_window: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    modalities: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String), nullable=True)
    has_vision: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    has_audio: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    has_tool_use: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    has_reasoning: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    coding_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    agent_capabilities: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String), nullable=True)
    api_availability: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    free_availability: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    free_limits: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB, nullable=True)
    price_per_million_tokens: Mapped[Optional[Decimal]] = mapped_column(nullable=True)
    price_per_image: Mapped[Optional[Decimal]] = mapped_column(nullable=True)
    price_per_video: Mapped[Optional[Decimal]] = mapped_column(nullable=True)
    speed_tokens_per_sec: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    last_verified: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    benchmark_scores: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB, nullable=True)
    item_metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column("metadata", JSONB, nullable=True)

    __table_args__ = (UniqueConstraint("provider", "model_id", name="uq_provider_model"),)


# ============================================================
# BENCHMARKS
# ============================================================

class Benchmark(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "benchmarks"

    model_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("ai_models.id"), nullable=False, index=True)
    task_type: Mapped[str] = mapped_column(String(100), nullable=False)
    task_name: Mapped[str] = mapped_column(String(255), nullable=False)
    task_description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    latency_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    cost_aud: Mapped[Optional[Decimal]] = mapped_column(nullable=True)
    score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    max_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    evaluator: Mapped[str] = mapped_column(String(100), nullable=False)
    result_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB, nullable=True)
    benchmark_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    # Relationships
    model: Mapped["AIModel"] = relationship(lazy="selectin")


# ============================================================
# MONITORING
# ============================================================

class Watchlist(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "watchlists"

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    watchlist_type: Mapped[WatchlistType] = mapped_column(SQLEnum(WatchlistType), nullable=False)
    query: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    filters: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB, nullable=True)
    interval_hours: Mapped[int] = mapped_column(Integer, default=24, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    last_run: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    next_run: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    alert_channels: Mapped[Optional[List[AlertChannel]]] = mapped_column(ARRAY(SQLEnum(AlertChannel)), nullable=True)
    alert_threshold: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB, nullable=True)

    # Relationships
    owner: Mapped["User"] = relationship(back_populates="watchlists", lazy="selectin")
    runs: Mapped[List["MonitorRun"]] = relationship(back_populates="watchlist", lazy="selectin")


class MonitorRun(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "monitor_runs"

    watchlist_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("watchlists.id"), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(50), default="pending", nullable=False)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    changes_detected: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    new_items: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    updated_items: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    removed_items: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    snapshot_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("snapshots.id"), nullable=True)

    # Relationships
    watchlist: Mapped["Watchlist"] = relationship(back_populates="runs", lazy="selectin")
    alerts: Mapped[List["Alert"]] = relationship(back_populates="monitor_run", lazy="selectin")


class Snapshot(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "snapshots"

    watchlist_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("watchlists.id"), nullable=False, index=True)
    data_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    item_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    data: Mapped[Dict[str, Any]] = mapped_column(JSONB, nullable=False)

    # Relationships
    monitor_runs: Mapped[List["MonitorRun"]] = relationship(back_populates="snapshot", lazy="selectin")


class Alert(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "alerts"

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    monitor_run_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("monitor_runs.id"), nullable=True, index=True)
    watchlist_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("watchlists.id"), nullable=True, index=True)
    channel: Mapped[AlertChannel] = mapped_column(SQLEnum(AlertChannel), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    severity: Mapped[str] = mapped_column(String(20), default="info", nullable=False)
    data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB, nullable=True)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_sent: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    user: Mapped["User"] = relationship(back_populates="alerts", lazy="selectin")
    monitor_run: Mapped[Optional["MonitorRun"]] = relationship(back_populates="alerts", lazy="selectin")


# ============================================================
# REPORTS
# ============================================================

class Report(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "reports"

    run_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("research_runs.id"), unique=True, nullable=False, index=True)
    executive_answer: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    bottom_line: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    best_options: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSONB, nullable=True)
    free_options: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSONB, nullable=True)
    cheap_options: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSONB, nullable=True)
    best_value: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSONB, nullable=True)
    similar_options: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSONB, nullable=True)
    alternatives: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSONB, nullable=True)
    marketplace_results: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSONB, nullable=True)
    businesses: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSONB, nullable=True)
    reviews: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSONB, nullable=True)
    community_feedback: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB, nullable=True)
    promotions: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSONB, nullable=True)
    pricing: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB, nullable=True)
    evidence: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSONB, nullable=True)
    contradictions: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSONB, nullable=True)
    risks: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String), nullable=True)
    unknown_information: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String), nullable=True)
    confidence: Mapped[float] = mapped_column(Float, default=0.5, nullable=False)
    last_verified: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    next_check: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    free_only_report: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB, nullable=True)

    # Relationships
    run: Mapped["ResearchRun"] = relationship(back_populates="report", lazy="selectin")


# ============================================================
# AUDIT
# ============================================================

class AuditEvent(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "audit_events"

    event_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("users.id"), nullable=True, index=True)
    run_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("research_runs.id"), nullable=True, index=True)
    provider: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    details: Mapped[Dict[str, Any]] = mapped_column(JSONB, nullable=False)
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    __table_args__ = (
        Index("ix_audit_events_created_at", "created_at"),
        Index("ix_audit_events_user_created", "user_id", "created_at"),
    )


# ============================================================
# AGENT RUNS
# ============================================================

class AgentRun(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "agent_runs"

    run_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("research_runs.id"), nullable=False, index=True)
    agent_name: Mapped[str] = mapped_column(String(100), nullable=False)
    agent_type: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="pending", nullable=False)
    input_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB, nullable=True)
    output_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB, nullable=True)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    tokens_used: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    cost_aud: Mapped[Decimal] = mapped_column(default=0, nullable=False)