"""
Unit Tests for ResearchOS FREE_ONLY & Security Policy Enforcement
"""
import pytest
from researchos.packages.core.config import OperatingMode
from researchos.packages.core.exceptions import FreePolicyViolationError
from researchos.packages.security.policy import FreePolicyEnforcer


def test_free_only_permits_free_provider():
    enforcer = FreePolicyEnforcer(mode=OperatingMode.FREE_ONLY)
    # A free provider with 0.0 cost must be authorized
    assert enforcer.authorize_execution("DuckDuckGo", is_free=True, estimated_cost_aud=0.0) is True
    assert "DuckDuckGo" in enforcer.executed_free_providers
    assert enforcer.current_session_spend_aud == 0.0


def test_free_only_blocks_paid_provider():
    enforcer = FreePolicyEnforcer(mode=OperatingMode.FREE_ONLY)
    # A provider with a non-zero cost MUST raise FreePolicyViolationError
    with pytest.raises(FreePolicyViolationError):
        enforcer.authorize_execution("PaidSearchAPI", is_free=False, estimated_cost_aud=0.05)


def test_local_only_blocks_cloud_endpoints():
    enforcer = FreePolicyEnforcer(mode=OperatingMode.LOCAL_ONLY)
    # Local Ollama must be allowed
    assert enforcer.authorize_execution("OllamaLocal", is_free=True, estimated_cost_aud=0.0) is True
    # Cloud providers must be blocked even if free
    with pytest.raises(FreePolicyViolationError):
        enforcer.authorize_execution("OpenRouter", is_free=True, estimated_cost_aud=0.0)


def test_audit_summary_reports_zero_spend():
    enforcer = FreePolicyEnforcer(mode=OperatingMode.FREE_ONLY)
    enforcer.authorize_execution("DuckDuckGo", is_free=True, estimated_cost_aud=0.0)
    enforcer.authorize_execution("GoogleNewsRSS", is_free=True, estimated_cost_aud=0.0)

    summary = enforcer.get_audit_summary()
    assert summary["mode"] == "FREE_ONLY"
    assert summary["actual_spend_aud"] == 0.0
    assert summary["paid_providers_count"] == 0
    assert summary["is_zero_spend_guaranteed"] is True
