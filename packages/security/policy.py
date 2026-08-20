"""
ResearchOS Free-First Central Security & Budget Policy Enforcer
"""
from typing import Dict, Any, Optional
from researchos.packages.core.config import OperatingMode, settings
from researchos.packages.core.exceptions import FreePolicyViolationError
from researchos.packages.core.logging import logger


class FreePolicyEnforcer:
    """
    Central non-negotiable security gateway.
    All search, AI, API, scraping and extraction calls MUST pass through this enforcer.
    """
    def __init__(self, mode: Optional[OperatingMode] = None):
        self.mode = mode or settings.OPERATING_MODE
        self.current_session_spend_aud: float = 0.0
        self.max_spend_aud: float = settings.MAX_SPEND_AUD
        self.executed_free_providers: set = set()
        self.executed_paid_providers: set = set()

    def set_mode(self, mode: OperatingMode):
        self.mode = mode

    def authorize_execution(self, provider_name: str, is_free: bool, estimated_cost_aud: float = 0.0) -> bool:
        """
        Determines whether a provider call is permitted under the active policy.
        Under FREE_ONLY:
            - is_free MUST be True
            - estimated_cost_aud MUST be 0.0
            - Unknown cost is strictly BLOCKED
        """
        # LOCAL_ONLY mode: only allow local endpoints (Ollama, LM Studio, local search/scrapers)
        if self.mode == OperatingMode.LOCAL_ONLY:
            is_local = "ollama" in provider_name.lower() or "lm_studio" in provider_name.lower() or "local" in provider_name.lower()
            if not is_local:
                logger.warning(f"[POLICY-BLOCKED] '{provider_name}' blocked under LOCAL_ONLY mode.")
                raise FreePolicyViolationError(
                    provider_name=provider_name,
                    estimated_cost=estimated_cost_aud,
                    message=f"LOCAL_ONLY Mode: Cloud provider '{provider_name}' is blocked."
                )
            return True

        # FREE_ONLY mode: Zero spend allowed
        if self.mode == OperatingMode.FREE_ONLY:
            if not is_free or estimated_cost_aud > 0.0:
                logger.warning(
                    f"[POLICY-BLOCKED] '{provider_name}' (Cost: ${estimated_cost_aud:.4f} AUD) blocked by FREE_ONLY policy."
                )
                raise FreePolicyViolationError(
                    provider_name=provider_name,
                    estimated_cost=estimated_cost_aud,
                    message=f"FREE_ONLY Policy Violation: '{provider_name}' requires payment (${estimated_cost_aud:.4f} AUD). Execution blocked."
                )
            self.executed_free_providers.add(provider_name)
            return True

        # FREE_FIRST mode: Free executed by default; paid require positive confirmation and budget check
        if self.mode == OperatingMode.FREE_FIRST:
            if not is_free and estimated_cost_aud > 0.0:
                if not settings.ALLOW_PAID_EXECUTION:
                    logger.warning(f"[POLICY-BLOCKED] '{provider_name}' blocked under FREE_FIRST because ALLOW_PAID_EXECUTION is False.")
                    raise FreePolicyViolationError(
                        provider_name=provider_name,
                        estimated_cost=estimated_cost_aud,
                        message=f"FREE_FIRST Mode: Paid execution for '{provider_name}' is currently disabled in settings."
                    )
                if self.current_session_spend_aud + estimated_cost_aud > self.max_spend_aud:
                    raise FreePolicyViolationError(
                        provider_name=provider_name,
                        estimated_cost=estimated_cost_aud,
                        message=f"Budget Exceeded: Remaining budget is ${(self.max_spend_aud - self.current_session_spend_aud):.4f} AUD."
                    )

        # CHEAP / FULL mode: check against budget cap
        if self.mode in [OperatingMode.CHEAP, OperatingMode.FULL]:
            if self.current_session_spend_aud + estimated_cost_aud > self.max_spend_aud:
                raise FreePolicyViolationError(
                    provider_name=provider_name,
                    estimated_cost=estimated_cost_aud,
                    message=f"Budget Cap Reached: Spend of ${(self.current_session_spend_aud + estimated_cost_aud):.4f} exceeds limit of ${self.max_spend_aud:.4f} AUD."
                )

        if is_free:
            self.executed_free_providers.add(provider_name)
        else:
            self.executed_paid_providers.add(provider_name)
            self.current_session_spend_aud += estimated_cost_aud
        return True

    def get_audit_summary(self) -> Dict[str, Any]:
        return {
            "mode": self.mode.value,
            "actual_spend_aud": round(self.current_session_spend_aud, 4),
            "free_providers_used": list(self.executed_free_providers),
            "paid_providers_used": list(self.executed_paid_providers),
            "paid_providers_count": len(self.executed_paid_providers),
            "is_zero_spend_guaranteed": self.mode == OperatingMode.FREE_ONLY,
        }


policy_enforcer = FreePolicyEnforcer()
