"""
ResearchOS Google Gemini Free Tier AI Connector
"""
import os
from typing import Any, Dict, List, Optional
import httpx
from researchos.packages.core.config import settings
from researchos.packages.core.logging import logger
from researchos.packages.core.schemas import ProviderStatus
from researchos.packages.providers.base import BaseAIProvider
from researchos.packages.security.policy import policy_enforcer


class GeminiAIProvider(BaseAIProvider):
    def __init__(self, api_key: Optional[str] = None):
        key = api_key or settings.GEMINI_API_KEY or os.environ.get("GEMINI_API_KEY")
        super().__init__(name="GoogleGemini", is_free=True, estimated_cost_aud=0.0)
        self.api_key = key
        self.endpoint = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"

    async def check_health(self) -> ProviderStatus:
        if not self.api_key:
            self.status = ProviderStatus.UNAVAILABLE
            return ProviderStatus.UNAVAILABLE
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models?key={self.api_key}"
            async with httpx.AsyncClient(timeout=8.0) as client:
                res = await client.get(url)
                if res.status_code == 200:
                    self.status = ProviderStatus.ONLINE
                elif res.status_code in (400, 401, 403):
                    self.status = ProviderStatus.AUTH_ERROR
                elif res.status_code == 429:
                    self.status = ProviderStatus.RATE_LIMITED
                else:
                    self.status = ProviderStatus.DEGRADED
        except Exception:
            self.status = ProviderStatus.UNAVAILABLE
        return self.status

    async def list_available_models(self) -> List[Dict[str, Any]]:
        return [
            {"id": "gemini-1.5-flash", "name": "Gemini 1.5 Flash", "context_length": 1048576, "is_free": True, "provider": "GoogleGemini"},
            {"id": "gemini-1.5-pro", "name": "Gemini 1.5 Pro", "context_length": 2097152, "is_free": True, "provider": "GoogleGemini"},
        ]

    async def generate_text(self, prompt: str, system_prompt: Optional[str] = None, model: Optional[str] = None, temperature: float = 0.2) -> str:
        policy_enforcer.authorize_execution(self.name, self.is_free, self.estimated_cost_aud)
        if not self.api_key:
            return ""

        model_name = model or "gemini-1.5-flash"
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={self.api_key}"

        contents = []
        if system_prompt:
            contents.append({"role": "user", "parts": [{"text": f"System Directive: {system_prompt}"}]})
        contents.append({"role": "user", "parts": [{"text": prompt}]})

        payload = {
            "contents": contents,
            "generationConfig": {"temperature": temperature},
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                res = await client.post(url, json=payload)
                if res.status_code == 200:
                    data = res.json()
                    candidates = data.get("candidates", [])
                    if candidates:
                        parts = candidates[0].get("content", {}).get("parts", [])
                        if parts:
                            return parts[0].get("text", "").strip()
                elif res.status_code == 429:
                    self.status = ProviderStatus.RATE_LIMITED
        except Exception as e:
            logger.error(f"Gemini generation error: {e}")

        return ""
