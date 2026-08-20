"""
ResearchOS Core Configuration
Centralized settings management with validation
"""
import os
from enum import Enum
from functools import lru_cache
from typing import List, Optional
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class OperatingMode(str, Enum):
    FREE_ONLY = "FREE_ONLY"
    FREE_FIRST = "FREE_FIRST"
    CHEAP = "CHEAP"
    FULL = "FULL"
    LOCAL_ONLY = "LOCAL_ONLY"


class ResearchDepth(str, Enum):
    QUICK = "quick"
    NORMAL = "normal"
    DEEP = "deep"
    MAXIMUM = "maximum"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    APP_NAME: str = "ResearchOS"
    APP_VERSION: str = "1.0.0"
    DEFAULT_LOCATION: str = "Brisbane, Queensland, Australia"

    # ============================================================
    # DATABASE
    # ============================================================
    DATABASE_URL: str = Field(
        default="sqlite:///data/researchos.db",
        description="Database connection URL (SQLite default, PostgreSQL supported in Docker)",
    )
    POSTGRES_PASSWORD: str = Field(
        default="researchos_dev_password", description="PostgreSQL password"
    )

    # ============================================================
    # REDIS
    # ============================================================
    REDIS_URL: str = Field(
        default="redis://localhost:6379/0", description="Redis connection URL"
    )

    # ============================================================
    # QDRANT VECTOR DATABASE
    # ============================================================
    QDRANT_URL: str = Field(
        default="http://localhost:6333", description="Qdrant connection URL"
    )

    # ============================================================
    # AI PROVIDER API KEYS
    # ============================================================
    GEMINI_API_KEY: Optional[str] = Field(default=None, description="Google Gemini API key")
    OPENROUTER_API_KEY: Optional[str] = Field(default=None, description="OpenRouter API key")

    # ============================================================
    # SEARCH PROVIDER API KEYS
    # ============================================================
    BRAVE_API_KEY: Optional[str] = Field(default=None, description="Brave Search API key")
    TAVILY_API_KEY: Optional[str] = Field(default=None, description="Tavily AI Search API key")
    EXA_API_KEY: Optional[str] = Field(default=None, description="Exa AI Search API key")
    SERPER_API_KEY: Optional[str] = Field(default=None, description="Serper Google Search API key")
    SERPAPI_API_KEY: Optional[str] = Field(default=None, description="SerpAPI key")

    # ============================================================
    # SOCIAL / CODE / VIDEO API KEYS
    # ============================================================
    GITHUB_TOKEN: Optional[str] = Field(default=None, description="GitHub Personal Access Token")
    YOUTUBE_API_KEY: Optional[str] = Field(default=None, description="YouTube Data API v3 key")

    # ============================================================
    # RESEARCHOS CORE SETTINGS
    # ============================================================
    OPERATING_MODE: OperatingMode = Field(default=OperatingMode.FREE_ONLY, description="Active operating mode")
    FREE_ONLY: bool = Field(default=True, description="Enforce $0 spend mode")
    MAX_SPEND_AUD: float = Field(default=0.0, description="Maximum spend in AUD")
    DEFAULT_CURRENCY: str = Field(default="AUD", description="Default currency")
    DEFAULT_COUNTRY: str = Field(default="AU", description="Default country code")
    DEFAULT_TIMEZONE: str = Field(default="Australia/Brisbane", description="Default timezone")

    # ============================================================
    # LOGGING
    # ============================================================
    LOG_LEVEL: str = Field(default="INFO", description="Log level")
    ENVIRONMENT: str = Field(default="development", description="Environment name")

    # ============================================================
    # OPTIONAL: NOTIFICATION WEBHOOKS
    # ============================================================
    DISCORD_WEBHOOK_URL: Optional[str] = Field(default=None, description="Discord webhook for alerts")
    TELEGRAM_BOT_TOKEN: Optional[str] = Field(default=None, description="Telegram bot token")
    TELEGRAM_CHAT_ID: Optional[str] = Field(default=None, description="Telegram chat ID")

    # ============================================================
    # OPTIONAL: EMAIL FOR ALERTS
    # ============================================================
    SMTP_HOST: Optional[str] = Field(default=None, description="SMTP host")
    SMTP_PORT: int = Field(default=587, description="SMTP port")
    SMTP_USER: Optional[str] = Field(default=None, description="SMTP username")
    SMTP_PASSWORD: Optional[str] = Field(default=None, description="SMTP password")
    ALERT_EMAIL_FROM: Optional[str] = Field(default=None, description="Alert email from address")
    ALERT_EMAIL_TO: Optional[str] = Field(default=None, description="Alert email to address")

    # ============================================================
    # OPTIONAL: SEARXNG INSTANCE
    # ============================================================
    SEARXNG_URL: Optional[str] = Field(default=None, description="Self-hosted SearXNG instance URL")

    # ============================================================
    # OPTIONAL: REDDIT API
    # ============================================================
    REDDIT_CLIENT_ID: Optional[str] = Field(default=None, description="Reddit client ID")
    REDDIT_CLIENT_SECRET: Optional[str] = Field(default=None, description="Reddit client secret")
    REDDIT_USER_AGENT: str = Field(default="ResearchOS/1.0", description="Reddit user agent")

    # ============================================================
    # OPTIONAL: HUGGINGFACE
    # ============================================================
    HUGGINGFACE_TOKEN: Optional[str] = Field(default=None, description="HuggingFace token")

    # ============================================================
    # OPTIONAL: LOCAL AI
    # ============================================================
    OLLAMA_HOST: str = Field(default="http://localhost:11434", description="Ollama host URL")
    OLLAMA_BASE_URL: str = Field(default="http://localhost:11434", description="Ollama base URL")
    LM_STUDIO_HOST: str = Field(default="http://localhost:1234", description="LM Studio host URL")
    LM_STUDIO_BASE_URL: str = Field(default="http://localhost:1234/v1", description="LM Studio base URL")

    @field_validator("DEFAULT_CURRENCY")
    @classmethod
    def validate_currency(cls, v: str) -> str:
        valid = ["AUD", "USD", "EUR", "GBP", "CAD", "NZD", "JPY"]
        if v.upper() not in valid:
            raise ValueError(f"Currency must be one of {valid}")
        return v.upper()

    @field_validator("DEFAULT_COUNTRY")
    @classmethod
    def validate_country(cls, v: str) -> str:
        if len(v) != 2:
            raise ValueError("Country must be 2-letter ISO code")
        return v.upper()

    @field_validator("LOG_LEVEL")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        valid = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid:
            raise ValueError(f"Log level must be one of {valid}")
        return v.upper()

    @field_validator("ENVIRONMENT")
    @classmethod
    def validate_env(cls, v: str) -> str:
        valid = ["development", "staging", "production"]
        if v.lower() not in valid:
            raise ValueError(f"Environment must be one of {valid}")
        return v.lower()

    @property
    def is_free_only(self) -> bool:
        """Check if FREE_ONLY mode is active"""
        return self.FREE_ONLY or self.MAX_SPEND_AUD <= 0

    @property
    def available_search_providers(self) -> List[str]:
        """Return list of configured search providers"""
        providers = []
        if self.BRAVE_API_KEY:
            providers.append("brave")
        if self.TAVILY_API_KEY:
            providers.append("tavily")
        if self.EXA_API_KEY:
            providers.append("exa")
        if self.SERPER_API_KEY:
            providers.append("serper")
        if self.SERPAPI_API_KEY:
            providers.append("serpapi")
        # DuckDuckGo and Google (HTML) don't need keys
        providers.extend(["duckduckgo", "google_html"])
        if self.SEARCHXNG_URL:
            providers.append("searxng")
        return providers

    @property
    def available_ai_providers(self) -> List[str]:
        """Return list of configured AI providers"""
        providers = []
        if self.GEMINI_API_KEY:
            providers.append("gemini")
        if self.OPENROUTER_API_KEY:
            providers.append("openrouter")
        # Local providers don't need keys
        providers.extend(["ollama", "lm_studio"])
        return providers


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()