"""
Providers routes - Provider management and configuration
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from uuid import UUID

from packages.core.database import get_db
from packages.core.logging import get_logger

router = APIRouter()
logger = get_logger("providers")


class ProviderCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    display_name: str = Field(..., min_length=1, max_length=255)
    provider_type: str = Field(..., pattern="^(SEARCH|AI|MARKETPLACE|BUSINESS|ACADEMIC|GOVERNMENT|SOCIAL|CODE)$")
    base_url: Optional[str] = None
    api_version: Optional[str] = None
    is_free: bool = False
    free_quota: Optional[int] = None
    free_quota_reset_period: Optional[str] = None
    pricing_info: Optional[Dict[str, Any]] = None
    billing_required: bool = False
    capabilities: Optional[List[str]] = None
    rate_limit_rpm: Optional[int] = None
    rate_limit_tpm: Optional[int] = None
    health_check_url: Optional[str] = None
    config_schema: Optional[Dict[str, Any]] = None
    is_enabled: bool = True
    priority: int = 0


class ProviderUpdate(BaseModel):
    display_name: Optional[str] = None
    base_url: Optional[str] = None
    api_version: Optional[str] = None
    is_free: Optional[bool] = None
    free_quota: Optional[int] = None
    free_quota_reset_period: Optional[str] = None
    pricing_info: Optional[Dict[str, Any]] = None
    billing_required: Optional[bool] = None
    capabilities: Optional[List[str]] = None
    rate_limit_rpm: Optional[int] = None
    rate_limit_tpm: Optional[int] = None
    health_check_url: Optional[str] = None
    config_schema: Optional[Dict[str, Any]] = None
    is_enabled: Optional[bool] = None
    priority: Optional[int] = None


class ProviderResponse(BaseModel):
    id: UUID
    name: str
    display_name: str
    provider_type: str
    base_url: Optional[str]
    api_version: Optional[str]
    status: str
    is_free: bool
    free_quota: Optional[int]
    free_quota_reset_period: Optional[str]
    pricing_info: Optional[Dict[str, Any]]
    billing_required: bool
    capabilities: Optional[List[str]]
    rate_limit_rpm: Optional[int]
    rate_limit_tpm: Optional[int]
    last_verified: Optional[str]
    last_success: Optional[str]
    last_failure: Optional[str]
    health_check_url: Optional[str]
    config_schema: Optional[Dict[str, Any]]
    is_enabled: bool
    priority: int
    created_at: str
    updated_at: str


@router.get("/", response_model=List[ProviderResponse])
async def list_providers(
    provider_type: Optional[str] = None,
    enabled_only: bool = True,
    db: AsyncSession = Depends(get_db),
):
    """List all providers"""
    from sqlalchemy import select
    from packages.core.models import Provider, ProviderType
    
    query = select(Provider)
    
    if provider_type:
        try:
            pt = ProviderType(provider_type.upper())
            query = query.where(Provider.provider_type == pt)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid provider type: {provider_type}")
    
    if enabled_only:
        query = query.where(Provider.is_enabled == True)
    
    query = query.order_by(Provider.priority.desc(), Provider.name)
    
    result = await db.execute(query)
    providers = result.scalars().all()
    
    return [
        ProviderResponse(
            id=p.id,
            name=p.name,
            display_name=p.display_name,
            provider_type=p.provider_type.value,
            base_url=p.base_url,
            api_version=p.api_version,
            status=p.status.value,
            is_free=p.is_free,
            free_quota=p.free_quota,
            free_quota_reset_period=p.free_quota_reset_period,
            pricing_info=p.pricing_info,
            billing_required=p.billing_required,
            capabilities=p.capabilities,
            rate_limit_rpm=p.rate_limit_rpm,
            rate_limit_tpm=p.rate_limit_tpm,
            last_verified=p.last_verified.isoformat() if p.last_verified else None,
            last_success=p.last_success.isoformat() if p.last_success else None,
            last_failure=p.last_failure.isoformat() if p.last_failure else None,
            health_check_url=p.health_check_url,
            config_schema=p.config_schema,
            is_enabled=p.is_enabled,
            priority=p.priority,
            created_at=p.created_at.isoformat(),
            updated_at=p.updated_at.isoformat(),
        )
        for p in providers
    ]


@router.post("/", response_model=ProviderResponse)
async def create_provider(provider: ProviderCreate, db: AsyncSession = Depends(get_db)):
    """Create a new provider"""
    from packages.core.models import Provider, ProviderType
    
    try:
        pt = ProviderType(provider.provider_type.upper())
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid provider type: {provider.provider_type}")
    
    new_provider = Provider(
        name=provider.name,
        display_name=provider.display_name,
        provider_type=pt,
        base_url=provider.base_url,
        api_version=provider.api_version,
        is_free=provider.is_free,
        free_quota=provider.free_quota,
        free_quota_reset_period=provider.free_quota_reset_period,
        pricing_info=provider.pricing_info,
        billing_required=provider.billing_required,
        capabilities=provider.capabilities,
        rate_limit_rpm=provider.rate_limit_rpm,
        rate_limit_tpm=provider.rate_limit_tpm,
        health_check_url=provider.health_check_url,
        config_schema=provider.config_schema,
        is_enabled=provider.is_enabled,
        priority=provider.priority,
    )
    
    db.add(new_provider)
    await db.commit()
    await db.refresh(new_provider)
    
    return ProviderResponse(
        id=new_provider.id,
        name=new_provider.name,
        display_name=new_provider.display_name,
        provider_type=new_provider.provider_type.value,
        base_url=new_provider.base_url,
        api_version=new_provider.api_version,
        status=new_provider.status.value,
        is_free=new_provider.is_free,
        free_quota=new_provider.free_quota,
        free_quota_reset_period=new_provider.free_quota_reset_period,
        pricing_info=new_provider.pricing_info,
        billing_required=new_provider.billing_required,
        capabilities=new_provider.capabilities,
        rate_limit_rpm=new_provider.rate_limit_rpm,
        rate_limit_tpm=new_provider.rate_limit_tpm,
        last_verified=new_provider.last_verified.isoformat() if new_provider.last_verified else None,
        last_success=new_provider.last_success.isoformat() if new_provider.last_success else None,
        last_failure=new_provider.last_failure.isoformat() if new_provider.last_failure else None,
        health_check_url=new_provider.health_check_url,
        config_schema=new_provider.config_schema,
        is_enabled=new_provider.is_enabled,
        priority=new_provider.priority,
        created_at=new_provider.created_at.isoformat(),
        updated_at=new_provider.updated_at.isoformat(),
    )


@router.get("/{provider_id}", response_model=ProviderResponse)
async def get_provider(provider_id: UUID, db: AsyncSession = Depends(get_db)):
    """Get provider by ID"""
    from sqlalchemy import select
    from packages.core.models import Provider
    
    result = await db.execute(select(Provider).where(Provider.id == provider_id))
    provider = result.scalar_one_or_none()
    
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")
    
    return ProviderResponse(
        id=provider.id,
        name=provider.name,
        display_name=provider.display_name,
        provider_type=provider.provider_type.value,
        base_url=provider.base_url,
        api_version=provider.api_version,
        status=provider.status.value,
        is_free=provider.is_free,
        free_quota=provider.free_quota,
        free_quota_reset_period=provider.free_quota_reset_period,
        pricing_info=provider.pricing_info,
        billing_required=provider.billing_required,
        capabilities=provider.capabilities,
        rate_limit_rpm=provider.rate_limit_rpm,
        rate_limit_tpm=provider.rate_limit_tpm,
        last_verified=provider.last_verified.isoformat() if provider.last_verified else None,
        last_success=provider.last_success.isoformat() if provider.last_success else None,
        last_failure=provider.last_failure.isoformat() if provider.last_failure else None,
        health_check_url=provider.health_check_url,
        config_schema=provider.config_schema,
        is_enabled=provider.is_enabled,
        priority=provider.priority,
        created_at=provider.created_at.isoformat(),
        updated_at=provider.updated_at.isoformat(),
    )


@router.patch("/{provider_id}", response_model=ProviderResponse)
async def update_provider(provider_id: UUID, update: ProviderUpdate, db: AsyncSession = Depends(get_db)):
    """Update a provider"""
    from sqlalchemy import select
    from packages.core.models import Provider
    
    result = await db.execute(select(Provider).where(Provider.id == provider_id))
    provider = result.scalar_one_or_none()
    
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")
    
    update_data = update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(provider, field, value)
    
    await db.commit()
    await db.refresh(provider)
    
    return ProviderResponse(
        id=provider.id,
        name=provider.name,
        display_name=provider.display_name,
        provider_type=provider.provider_type.value,
        base_url=provider.base_url,
        api_version=provider.api_version,
        status=provider.status.value,
        is_free=provider.is_free,
        free_quota=provider.free_quota,
        free_quota_reset_period=provider.free_quota_reset_period,
        pricing_info=provider.pricing_info,
        billing_required=provider.billing_required,
        capabilities=provider.capabilities,
        rate_limit_rpm=provider.rate_limit_rpm,
        rate_limit_tpm=provider.rate_limit_tpm,
        last_verified=provider.last_verified.isoformat() if provider.last_verified else None,
        last_success=provider.last_success.isoformat() if provider.last_success else None,
        last_failure=provider.last_failure.isoformat() if provider.last_failure else None,
        health_check_url=provider.health_check_url,
        config_schema=provider.config_schema,
        is_enabled=provider.is_enabled,
        priority=provider.priority,
        created_at=provider.created_at.isoformat(),
        updated_at=provider.updated_at.isoformat(),
    )


@router.delete("/{provider_id}")
async def delete_provider(provider_id: UUID, db: AsyncSession = Depends(get_db)):
    """Delete a provider"""
    from sqlalchemy import select
    from packages.core.models import Provider
    
    result = await db.execute(select(Provider).where(Provider.id == provider_id))
    provider = result.scalar_one_or_none()
    
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")
    
    await db.delete(provider)
    await db.commit()
    
    return {"success": True, "message": "Provider deleted"}


@router.post("/{provider_id}/test")
async def test_provider(provider_id: UUID, db: AsyncSession = Depends(get_db)):
    """Test a provider connection"""
    from sqlalchemy import select
    from packages.core.models import Provider
    
    result = await db.execute(select(Provider).where(Provider.id == provider_id))
    provider = result.scalar_one_or_none()
    
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")
    
    # TODO: Implement actual provider test
    return {
        "provider": provider.name,
        "success": False,
        "message": "Provider testing not yet implemented",
    }