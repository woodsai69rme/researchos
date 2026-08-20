"""
ResearchOS Core Custom Exceptions
"""

class ResearchOSError(Exception):
    """Base class for all ResearchOS exceptions."""
    pass


class FreePolicyViolationError(ResearchOSError):
    """Raised when an operation attempts to execute paid APIs or incur costs under FREE_ONLY mode."""
    def __init__(self, provider_name: str, estimated_cost: float = 0.0, message: str = ""):
        self.provider_name = provider_name
        self.estimated_cost = estimated_cost
        super().__init__(
            message or f"FREE_ONLY Policy Blocked: Attempted to call paid/metered provider '{provider_name}' with cost {estimated_cost:.4f} AUD."
        )


class QuotaExhaustedError(ResearchOSError):
    """Raised when a provider's free quota is reached."""
    pass


class ProviderUnavailableError(ResearchOSError):
    """Raised when a provider service is offline or unreachable."""
    pass


class SSRFSecurityError(ResearchOSError):
    """Raised when an outbound URL target violates local/private network isolation rules."""
    pass


class PromptInjectionDetectedError(ResearchOSError):
    """Raised when hostile prompt override instructions are detected in retrieved content."""
    pass
