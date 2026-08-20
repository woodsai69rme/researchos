"""
ResearchOS Ollama Local AI Inference Connector
"""
from typing import Any, Dict, List, Optional
import httpx
from researchos.packages.core.config import settings
from researchos.packages.core.logging import logger
from researchos.packages.core.schemas import ProviderStatus
from researchos.packages.providers.base import BaseAIProvider
from researchos.packages.security.policy import policy_enforcer


class OllamaAIProvider(BaseAIProvider):
    def __init__(self, base_url: Optional[str] = None):
        super().__init__(name="OllamaLocal", is_free=True, estimated_cost_aud=0.0)
        self.base_url = base_url or settings.OLLAMA_BASE_URL

    async def check_health(self) -> ProviderStatus:
        try:
            async with httpx.AsyncClient(timeout=4.0) as client:
                res = await client.get(f"{self.base_url}/api/tags")
                if res.status_code == 200:
                    self.status = ProviderStatus.ONLINE
                    return ProviderStatus.ONLINE
        except Exception as e:
            logger.debug(f"Ollama local service unavailable at {self.base_url}: {e}")
            self.status = ProviderStatus.UNAVAILABLE
        return self.status

    async def list_available_models(self) -> List[Dict[str, Any]]:
        models = []
        try:
            async with httpx.AsyncClient(timeout=4.0) as client:
                res = await client.get(f"{self.base_url}/api/tags")
                if res.status_code == 200:
                    data = res.json()
                    for m in data.get("models", []):
                        models.append({
                            "id": m.get("name"),
                            "name": m.get("name"),
                            "size_bytes": m.get("size", 0),
                            "is_free": True,
                            "provider": "OllamaLocal",
                        })
        except Exception:
            pass
        return models

    async def generate_text(self, prompt: str, system_prompt: Optional[str] = None, model: Optional[str] = None, temperature: float = 0.2) -> str:
        policy_enforcer.authorize_execution(self.name, self.is_free, self.estimated_cost_aud)
        
        # Pick default available model
        target_model = model or "ornith-1.0-9b:q4_k_m"
        
        payload = {
            "model": target_model,
            "prompt": prompt,
            "system": system_prompt or "You are ResearchOS, an accurate research synthesis engine.",
            "stream": False,
            "options": {"temperature": temperature},
        }

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                res = await client.post(f"{self.base_url}/api/generate", json=payload)
                if res.status_code == 200:
                    return res.json().get("response", "").strip()
                else:
                    logger.warning(f"Ollama generate error code {res.status_code}")
        except Exception as e:
            logger.warning(f"Ollama generation failed: {e}")

        return ""
