"""
ResearchOS OpenRouter AI Provider Connector with Verified Free Model Support
"""
from typing import Any, Dict, List, Optional
import httpx
from researchos.packages.core.config import settings
from researchos.packages.core.logging import logger
from researchos.packages.core.schemas import ProviderStatus
from researchos.packages.providers.base import BaseAIProvider
from researchos.packages.security.policy import policy_enforcer


class OpenRouterAIProvider(BaseAIProvider):
    # Known active 100% free model endpoints on OpenRouter
    KNOWN_FREE_MODELS = [
        "google/gemma-4-26b-a4b-it:free",
        "nvidia/nemotron-nano-12b-v2-vl:free",
        "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free",
        "meta-llama/llama-3.3-70b-instruct:free",
        "deepseek/deepseek-r1:free",
        "qwen/qwen-2.5-coder-32b-instruct:free",
        "mistralai/mistral-7b-instruct:free",
    ]

    def __init__(self, api_key: Optional[str] = None):
        key = api_key or settings.OPENROUTER_API_KEY or os.environ.get("OPENROUTER_API_KEY")
        super().__init__(name="OpenRouter", is_free=True, estimated_cost_aud=0.0)
        self.api_key = key
        self.endpoint = "https://openrouter.ai/api/v1/chat/completions"
        self.models_endpoint = "https://openrouter.ai/api/v1/models"

    async def check_health(self) -> ProviderStatus:
        if not self.api_key:
            self.status = ProviderStatus.UNAVAILABLE
            return ProviderStatus.UNAVAILABLE
        try:
            headers = {"Authorization": f"Bearer {self.api_key}"}
            async with httpx.AsyncClient(timeout=8.0) as client:
                res = await client.get(self.models_endpoint, headers=headers)
                if res.status_code == 200:
                    self.status = ProviderStatus.ONLINE
                elif res.status_code in (401, 403):
                    self.status = ProviderStatus.AUTH_ERROR
                else:
                    self.status = ProviderStatus.DEGRADED
        except Exception:
            self.status = ProviderStatus.UNAVAILABLE
        return self.status

    async def list_available_models(self) -> List[Dict[str, Any]]:
        free_models = []
        try:
            headers = {"Authorization": f"Bearer {self.api_key}"} if self.api_key else {}
            async with httpx.AsyncClient(timeout=10.0) as client:
                res = await client.get(self.models_endpoint, headers=headers)
                if res.status_code == 200:
                    data = res.json()
                    for m in data.get("data", []):
                        m_id = m.get("id", "")
                        pricing = m.get("pricing", {})
                        prompt_price = float(pricing.get("prompt", 0))
                        completion_price = float(pricing.get("completion", 0))
                        is_free = (prompt_price == 0.0 and completion_price == 0.0) or ":free" in m_id

                        if is_free:
                            free_models.append({
                                "id": m_id,
                                "name": m.get("name", m_id),
                                "context_length": m.get("context_length", 128000),
                                "is_free": True,
                                "provider": "OpenRouter",
                            })
        except Exception as e:
            logger.warning(f"Error fetching OpenRouter models: {e}")
            for fm in self.KNOWN_FREE_MODELS:
                free_models.append({"id": fm, "name": fm, "context_length": 128000, "is_free": True, "provider": "OpenRouter"})
        return free_models

    async def generate_text(self, prompt: str, system_prompt: Optional[str] = None, model: Optional[str] = None, temperature: float = 0.2) -> str:
        policy_enforcer.authorize_execution(self.name, self.is_free, self.estimated_cost_aud)
        if not self.api_key:
            return ""

        target_model = model or "google/gemma-4-26b-a4b-it:free"
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "https://researchos.local",
            "X-Title": "ResearchOS",
            "Content-Type": "application/json",
        }

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": target_model,
            "messages": messages,
            "temperature": temperature,
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                res = await client.post(self.endpoint, headers=headers, json=payload)
                if res.status_code == 200:
                    data = res.json()
                    choices = data.get("choices", [])
                    if choices:
                        return choices[0].get("message", {}).get("content", "").strip()
                elif res.status_code == 429:
                    logger.warning(f"OpenRouter rate limit reached for {target_model}")
                    self.status = ProviderStatus.RATE_LIMITED
        except Exception as e:
            logger.error(f"OpenRouter generation failure: {e}")

        return ""
