"""
AI Provider Adapters
Base classes and implementations for AI providers (LLMs, embeddings, etc.)
"""
import abc
import asyncio
import json
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, AsyncGenerator, Union

import httpx

from packages.core.config import settings
from packages.core.logging import get_logger
from packages.core.security import free_policy_engine, sanitize_for_llm


logger = get_logger("ai_providers")


@dataclass
class AIMessage:
    """Standardized message format"""
    role: str  # system, user, assistant, tool
    content: str
    name: Optional[str] = None
    tool_calls: Optional[List[Dict[str, Any]]] = None
    tool_call_id: Optional[str] = None


@dataclass
class AIResponse:
    """Standardized AI response"""
    content: str
    model: str
    provider: str
    usage: Dict[str, int] = field(default_factory=dict)  # prompt_tokens, completion_tokens, total_tokens
    finish_reason: Optional[str] = None
    tool_calls: Optional[List[Dict[str, Any]]] = None
    raw_response: Dict[str, Any] = field(default_factory=dict)
    cost_aud: float = 0.0


@dataclass
class EmbeddingResponse:
    """Standardized embedding response"""
    embeddings: List[List[float]]
    model: str
    provider: str
    usage: Dict[str, int] = field(default_factory=dict)
    cost_aud: float = 0.0


@dataclass
class ProviderCapabilities:
    """AI provider capabilities"""
    supports_chat: bool = True
    supports_completion: bool = False
    supports_embeddings: bool = False
    supports_function_calling: bool = False
    supports_vision: bool = False
    supports_audio: bool = False
    supports_streaming: bool = True
    max_context_window: int = 4096
    max_output_tokens: int = 4096
    rate_limit_rpm: int = 60
    rate_limit_tpm: int = 100000
    requires_api_key: bool = True
    is_free: bool = False
    free_models: List[str] = field(default_factory=list)
    free_tier_limits: Dict[str, Any] = field(default_factory=dict)


class AIProvider(abc.ABC):
    """Abstract base class for AI providers"""
    
    name: str = "base"
    display_name: str = "Base AI Provider"
    capabilities = ProviderCapabilities()
    
    def __init__(self, api_key: Optional[str] = None, **kwargs):
        self.api_key = api_key
        self.config = kwargs
        self.client = httpx.AsyncClient(timeout=120.0)
        self._request_count = 0
        self._token_count = 0
        self._last_request_time = 0.0
        self._last_token_reset = time.time()
    
    @abc.abstractmethod
    async def chat(
        self,
        messages: List[AIMessage],
        model: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        stream: bool = False,
        **kwargs
    ) -> Union[AIResponse, AsyncGenerator[AIResponse, None]]:
        """Chat completion"""
        pass
    
    @abc.abstractmethod
    async def embed(
        self,
        texts: List[str],
        model: str,
        **kwargs
    ) -> EmbeddingResponse:
        """Generate embeddings"""
        pass
    
    @abc.abstractmethod
    async def list_models(self) -> List[Dict[str, Any]]:
        """List available models"""
        pass
    
    @abc.abstractmethod
    async def health_check(self) -> bool:
        """Check if provider is healthy"""
        pass
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()
    
    def _rate_limit(self):
        """Rate limiting for requests and tokens"""
        now = time.time()
        
        # Reset token counter per minute
        if now - self._last_token_reset >= 60:
            self._token_count = 0
            self._last_token_reset = now
        
        # Request rate limit
        min_interval = 60.0 / self.capabilities.rate_limit_rpm
        elapsed = now - self._last_request_time
        if elapsed < min_interval:
            time.sleep(min_interval - elapsed)
        
        self._last_request_time = time.time()
        self._request_count += 1
    
    def _check_token_budget(self, estimated_tokens: int) -> bool:
        """Check if we have token budget"""
        return (self._token_count + estimated_tokens) <= self.capabilities.rate_limit_tpm
    
    def _record_tokens(self, tokens: int):
        """Record token usage"""
        self._token_count += tokens


class GeminiProvider(AIProvider):
    """Google Gemini API provider"""
    
    name = "gemini"
    display_name = "Google Gemini"
    capabilities = ProviderCapabilities(
        supports_chat=True,
        supports_embeddings=True,
        supports_function_calling=True,
        supports_vision=True,
        supports_audio=True,
        supports_streaming=True,
        max_context_window=1000000,  # 1M for Gemini 1.5 Pro
        max_output_tokens=8192,
        rate_limit_rpm=60,
        rate_limit_tpm=1000000,
        requires_api_key=True,
        is_free=True,  # Free tier available
        free_models=["gemini-1.5-flash", "gemini-1.5-pro", "gemini-pro"],
        free_tier_limits={"rpm": 15, "tpm": 1000000, "rpd": 1500},
    )
    
    BASE_URL = "https://generativelanguage.googleapis.com/v1beta"
    
    def __init__(self, api_key: Optional[str] = None, **kwargs):
        super().__init__(api_key, **kwargs)
        if not self.api_key:
            self.api_key = settings.GEMINI_API_KEY
    
    def _format_messages(self, messages: List[AIMessage]) -> List[Dict[str, Any]]:
        """Convert messages to Gemini format"""
        formatted = []
        for msg in messages:
            if msg.role == "system":
                # Gemini uses system_instruction separately
                continue
            role = "user" if msg.role == "user" else "model"
            formatted.append({
                "role": role,
                "parts": [{"text": msg.content}]
            })
        return formatted
    
    async def chat(
        self,
        messages: List[AIMessage],
        model: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        stream: bool = False,
        **kwargs
    ) -> Union[AIResponse, AsyncGenerator[AIResponse, None]]:
        if not self.api_key:
            raise ValueError("Gemini API key required")
        
        self._rate_limit()
        
        # Extract system message
        system_instruction = None
        user_messages = []
        for msg in messages:
            if msg.role == "system":
                system_instruction = msg.content
            else:
                user_messages.append(msg)
        
        url = f"{self.BASE_URL}/models/{model}:generateContent"
        if stream:
            url = f"{self.BASE_URL}/models/{model}:streamGenerateContent"
        
        payload = {
            "contents": self._format_messages(user_messages),
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens or self.capabilities.max_output_tokens,
                "topP": 0.95,
                "topK": 40,
            },
        }
        
        if system_instruction:
            payload["systemInstruction"] = {"parts": [{"text": system_instruction}]}
        
        if tools:
            payload["tools"] = [{"functionDeclarations": tools}]
        
        headers = {
            "Content-Type": "application/json",
            "x-goog-api-key": self.api_key,
        }
        
        try:
            if stream:
                return self._stream_chat(url, payload, headers, model)
            else:
                response = await self.client.post(url, json=payload, headers=headers)
                response.raise_for_status()
                data = response.json()
                
                return self._parse_response(data, model)
                
        except httpx.HTTPStatusError as e:
            logger.error("Gemini chat failed", error=str(e), status=e.response.status_code)
            raise
        except Exception as e:
            logger.error("Gemini chat error", error=str(e))
            raise
    
    async def _stream_chat(
        self,
        url: str,
        payload: Dict,
        headers: Dict,
        model: str
    ) -> AsyncGenerator[AIResponse, None]:
        """Stream chat responses"""
        async with self.client.stream("POST", url, json=payload, headers=headers) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    data = json.loads(line[6:])
                    if "candidates" in data:
                        yield self._parse_response(data, model)
    
    def _parse_response(self, data: Dict, model: str) -> AIResponse:
        """Parse Gemini response"""
        candidate = data.get("candidates", [{}])[0]
        content = candidate.get("content", {})
        parts = content.get("parts", [])
        
        text_content = ""
        tool_calls = []
        
        for part in parts:
            if "text" in part:
                text_content += part["text"]
            elif "functionCall" in part:
                tool_calls.append({
                    "id": part["functionCall"].get("name", ""),
                    "name": part["functionCall"].get("name", ""),
                    "arguments": part["functionCall"].get("args", {}),
                })
        
        usage = data.get("usageMetadata", {})
        
        return AIResponse(
            content=text_content,
            model=model,
            provider=self.name,
            usage={
                "prompt_tokens": usage.get("promptTokenCount", 0),
                "completion_tokens": usage.get("candidatesTokenCount", 0),
                "total_tokens": usage.get("totalTokenCount", 0),
            },
            finish_reason=candidate.get("finishReason"),
            tool_calls=tool_calls if tool_calls else None,
            raw_response=data,
            cost_aud=0.0,  # Free tier
        )
    
    async def embed(
        self,
        texts: List[str],
        model: str = "text-embedding-004",
        **kwargs
    ) -> EmbeddingResponse:
        if not self.api_key:
            raise ValueError("Gemini API key required")
        
        self._rate_limit()
        
        url = f"{self.BASE_URL}/models/{model}:embedContent"
        
        payload = {
            "content": {"parts": [{"text": t} for t in texts]},
        }
        
        headers = {
            "Content-Type": "application/json",
            "x-goog-api-key": self.api_key,
        }
        
        try:
            response = await self.client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            embeddings = [item["values"] for item in data.get("embedding", [])]
            
            return EmbeddingResponse(
                embeddings=embeddings,
                model=model,
                provider=self.name,
                usage={"total_tokens": len(texts) * 100},  # Estimate
                cost_aud=0.0,
            )
            
        except Exception as e:
            logger.error("Gemini embed error", error=str(e))
            raise
    
    async def list_models(self) -> List[Dict[str, Any]]:
        if not self.api_key:
            return []
        
        try:
            response = await self.client.get(
                f"{self.BASE_URL}/models",
                params={"key": self.api_key},
            )
            response.raise_for_status()
            data = response.json()
            
            models = []
            for m in data.get("models", []):
                models.append({
                    "id": m["name"].replace("models/", ""),
                    "name": m.get("displayName", m["name"]),
                    "description": m.get("description"),
                    "input_token_limit": m.get("inputTokenLimit"),
                    "output_token_limit": m.get("outputTokenLimit"),
                    "supported_generation_methods": m.get("supportedGenerationMethods", []),
                })
            
            return models
            
        except Exception as e:
            logger.error("Gemini list_models error", error=str(e))
            return []
    
    async def health_check(self) -> bool:
        if not self.api_key:
            return False
        try:
            response = await self.client.get(
                f"{self.BASE_URL}/models",
                params={"key": self.api_key},
            )
            return response.status_code == 200
        except Exception:
            return False


class OpenRouterProvider(AIProvider):
    """OpenRouter API provider (access to many models)"""
    
    name = "openrouter"
    display_name = "OpenRouter"
    capabilities = ProviderCapabilities(
        supports_chat=True,
        supports_function_calling=True,
        supports_vision=True,
        supports_streaming=True,
        max_context_window=200000,  # Varies by model
        max_output_tokens=4096,
        rate_limit_rpm=60,
        rate_limit_tpm=200000,
        requires_api_key=True,
        is_free=False,  # Has free models but requires credits
        free_models=[
            "google/gemma-4-26b-a4b-it:free",
            "nvidia/nemotron-nano-12b-v2-vl:free",
            "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free",
            "meta-llama/llama-3.1-8b-instruct:free",
        ],
    )
    
    BASE_URL = "https://openrouter.ai/api/v1"
    
    def __init__(self, api_key: Optional[str] = None, **kwargs):
        super().__init__(api_key, **kwargs)
        if not self.api_key:
            self.api_key = settings.OPENROUTER_API_KEY
    
    async def chat(
        self,
        messages: List[AIMessage],
        model: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        stream: bool = False,
        **kwargs
    ) -> Union[AIResponse, AsyncGenerator[AIResponse, None]]:
        if not self.api_key:
            raise ValueError("OpenRouter API key required")
        
        self._rate_limit()
        
        # Sanitize messages for LLM
        sanitized_messages = []
        for msg in messages:
            sanitized_messages.append({
                "role": msg.role,
                "content": sanitize_for_llm(msg.content),
            })
        
        payload = {
            "model": model,
            "messages": sanitized_messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": stream,
        }
        
        if tools:
            payload["tools"] = tools
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://researchos.local",
            "X-Title": "ResearchOS",
        }
        
        try:
            if stream:
                return self._stream_chat(payload, headers, model)
            else:
                response = await self.client.post(
                    f"{self.BASE_URL}/chat/completions",
                    json=payload,
                    headers=headers,
                )
                response.raise_for_status()
                data = response.json()
                
                return self._parse_response(data, model)
                
        except httpx.HTTPStatusError as e:
            logger.error("OpenRouter chat failed", error=str(e), status=e.response.status_code)
            raise
        except Exception as e:
            logger.error("OpenRouter chat error", error=str(e))
            raise
    
    async def _stream_chat(
        self,
        payload: Dict,
        headers: Dict,
        model: str
    ) -> AsyncGenerator[AIResponse, None]:
        """Stream chat responses"""
        async with self.client.stream(
            "POST",
            f"{self.BASE_URL}/chat/completions",
            json=payload,
            headers=headers,
        ) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    if line[6:].strip() == "[DONE]":
                        break
                    try:
                        data = json.loads(line[6:])
                        yield self._parse_stream_chunk(data, model)
                    except json.JSONDecodeError:
                        continue
    
    def _parse_response(self, data: Dict, model: str) -> AIResponse:
        """Parse OpenRouter response"""
        choice = data.get("choices", [{}])[0]
        message = choice.get("message", {})
        
        return AIResponse(
            content=message.get("content", ""),
            model=model,
            provider=self.name,
            usage=data.get("usage", {}),
            finish_reason=choice.get("finish_reason"),
            tool_calls=message.get("tool_calls"),
            raw_response=data,
            cost_aud=0.0,  # Will be calculated based on model pricing
        )
    
    def _parse_stream_chunk(self, data: Dict, model: str) -> AIResponse:
        """Parse streaming chunk"""
        choice = data.get("choices", [{}])[0]
        delta = choice.get("delta", {})
        
        return AIResponse(
            content=delta.get("content", ""),
            model=model,
            provider=self.name,
            usage={},
            finish_reason=choice.get("finish_reason"),
            tool_calls=delta.get("tool_calls"),
            raw_response=data,
            cost_aud=0.0,
        )
    
    async def embed(
        self,
        texts: List[str],
        model: str = "text-embedding-3-small",
        **kwargs
    ) -> EmbeddingResponse:
        if not self.api_key:
            raise ValueError("OpenRouter API key required")
        
        # OpenRouter doesn't directly support embeddings, would need specific model
        raise NotImplementedError("Embeddings not directly supported via OpenRouter")
    
    async def list_models(self) -> List[Dict[str, Any]]:
        if not self.api_key:
            return []
        
        try:
            response = await self.client.get(
                f"{self.BASE_URL}/models",
                headers={"Authorization": f"Bearer {self.api_key}"},
            )
            response.raise_for_status()
            data = response.json()
            
            models = []
            for m in data.get("data", []):
                models.append({
                    "id": m["id"],
                    "name": m.get("name", m["id"]),
                    "description": m.get("description"),
                    "context_length": m.get("context_length"),
                    "pricing": m.get("pricing"),
                    "architecture": m.get("architecture"),
                })
            
            return models
            
        except Exception as e:
            logger.error("OpenRouter list_models error", error=str(e))
            return []
    
    async def health_check(self) -> bool:
        if not self.api_key:
            return False
        try:
            response = await self.client.get(
                f"{self.BASE_URL}/models",
                headers={"Authorization": f"Bearer {self.api_key}"},
            )
            return response.status_code == 200
        except Exception:
            return False


class OllamaProvider(AIProvider):
    """Ollama local AI provider"""
    
    name = "ollama"
    display_name = "Ollama (Local)"
    capabilities = ProviderCapabilities(
        supports_chat=True,
        supports_embeddings=True,
        supports_function_calling=False,  # Limited
        supports_streaming=True,
        max_context_window=32768,  # Varies by model
        max_output_tokens=4096,
        rate_limit_rpm=1000,  # Local, no real limit
        rate_limit_tpm=1000000,
        requires_api_key=False,
        is_free=True,
        free_models=[],  # Dynamic based on what's pulled
    )
    
    def __init__(self, api_key: Optional[str] = None, host: str = None, **kwargs):
        super().__init__(api_key, **kwargs)
        self.host = host or settings.OLLAMA_HOST
        self.BASE_URL = f"{self.host}/api"
    
    async def chat(
        self,
        messages: List[AIMessage],
        model: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        stream: bool = False,
        **kwargs
    ) -> Union[AIResponse, AsyncGenerator[AIResponse, None]]:
        self._rate_limit()
        
        # Convert messages to Ollama format
        ollama_messages = []
        for msg in messages:
            ollama_messages.append({
                "role": msg.role,
                "content": msg.content,
            })
        
        payload = {
            "model": model,
            "messages": ollama_messages,
            "stream": stream,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens or -1,
            },
        }
        
        if tools:
            # Ollama doesn't support tools natively yet
            pass
        
        try:
            if stream:
                return self._stream_chat(payload, model)
            else:
                response = await self.client.post(
                    f"{self.BASE_URL}/chat",
                    json=payload,
                )
                response.raise_for_status()
                data = response.json()
                
                return self._parse_response(data, model)
                
        except Exception as e:
            logger.error("Ollama chat error", error=str(e))
            raise
    
    async def _stream_chat(
        self,
        payload: Dict,
        model: str
    ) -> AsyncGenerator[AIResponse, None]:
        """Stream chat responses"""
        async with self.client.stream(
            "POST",
            f"{self.BASE_URL}/chat",
            json=payload,
        ) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if line.strip():
                    try:
                        data = json.loads(line)
                        if not data.get("done", False):
                            yield AIResponse(
                                content=data.get("message", {}).get("content", ""),
                                model=model,
                                provider=self.name,
                                usage={},
                                finish_reason=None,
                                raw_response=data,
                                cost_aud=0.0,
                            )
                        else:
                            yield AIResponse(
                                content="",
                                model=model,
                                provider=self.name,
                                usage={
                                    "prompt_tokens": data.get("prompt_eval_count", 0),
                                    "completion_tokens": data.get("eval_count", 0),
                                    "total_tokens": data.get("prompt_eval_count", 0) + data.get("eval_count", 0),
                                },
                                finish_reason="stop",
                                raw_response=data,
                                cost_aud=0.0,
                            )
                    except json.JSONDecodeError:
                        continue
    
    def _parse_response(self, data: Dict, model: str) -> AIResponse:
        """Parse Ollama response"""
        return AIResponse(
            content=data.get("message", {}).get("content", ""),
            model=model,
            provider=self.name,
            usage={
                "prompt_tokens": data.get("prompt_eval_count", 0),
                "completion_tokens": data.get("eval_count", 0),
                "total_tokens": data.get("prompt_eval_count", 0) + data.get("eval_count", 0),
            },
            finish_reason="stop" if data.get("done") else None,
            raw_response=data,
            cost_aud=0.0,
        )
    
    async def embed(
        self,
        texts: List[str],
        model: str = "nomic-embed-text",
        **kwargs
    ) -> EmbeddingResponse:
        self._rate_limit()
        
        embeddings = []
        total_tokens = 0
        
        for text in texts:
            response = await self.client.post(
                f"{self.BASE_URL}/embeddings",
                json={"model": model, "prompt": text},
            )
            response.raise_for_status()
            data = response.json()
            embeddings.append(data.get("embedding", []))
            total_tokens += len(text) // 4  # Rough estimate
        
        return EmbeddingResponse(
            embeddings=embeddings,
            model=model,
            provider=self.name,
            usage={"total_tokens": total_tokens},
            cost_aud=0.0,
        )
    
    async def list_models(self) -> List[Dict[str, Any]]:
        try:
            response = await self.client.get(f"{self.BASE_URL}/tags")
            response.raise_for_status()
            data = response.json()
            
            models = []
            for m in data.get("models", []):
                models.append({
                    "id": m["name"],
                    "name": m["name"],
                    "size": m.get("size"),
                    "modified_at": m.get("modified_at"),
                    "digest": m.get("digest"),
                    "details": m.get("details", {}),
                })
            
            return models
            
        except Exception as e:
            logger.error("Ollama list_models error", error=str(e))
            return []
    
    async def health_check(self) -> bool:
        try:
            response = await self.client.get(f"{self.BASE_URL}/tags")
            return response.status_code == 200
        except Exception:
            return False
    
    async def pull_model(self, model: str) -> AsyncGenerator[Dict[str, Any], None]:
        """Pull a model"""
        async with self.client.stream(
            "POST",
            f"{self.BASE_URL}/pull",
            json={"name": model, "stream": True},
        ) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if line.strip():
                    yield json.loads(line)


class LMStudioProvider(AIProvider):
    """LM Studio local AI provider (OpenAI-compatible API)"""
    
    name = "lm_studio"
    display_name = "LM Studio (Local)"
    capabilities = ProviderCapabilities(
        supports_chat=True,
        supports_embeddings=True,
        supports_function_calling=True,
        supports_streaming=True,
        max_context_window=32768,
        max_output_tokens=4096,
        rate_limit_rpm=1000,
        rate_limit_tpm=1000000,
        requires_api_key=False,
        is_free=True,
    )
    
    def __init__(self, api_key: Optional[str] = None, host: str = None, **kwargs):
        super().__init__(api_key, **kwargs)
        self.host = host or settings.LM_STUDIO_HOST
        self.BASE_URL = f"{self.host}/v1"
    
    async def chat(
        self,
        messages: List[AIMessage],
        model: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        stream: bool = False,
        **kwargs
    ) -> Union[AIResponse, AsyncGenerator[AIResponse, None]]:
        self._rate_limit()
        
        sanitized_messages = []
        for msg in messages:
            sanitized_messages.append({
                "role": msg.role,
                "content": sanitize_for_llm(msg.content),
            })
        
        payload = {
            "model": model,
            "messages": sanitized_messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": stream,
        }
        
        if tools:
            payload["tools"] = tools
        
        try:
            if stream:
                return self._stream_chat(payload, model)
            else:
                response = await self.client.post(
                    f"{self.BASE_URL}/chat/completions",
                    json=payload,
                )
                response.raise_for_status()
                data = response.json()
                
                return self._parse_response(data, model)
                
        except Exception as e:
            logger.error("LM Studio chat error", error=str(e))
            raise
    
    async def _stream_chat(
        self,
        payload: Dict,
        model: str
    ) -> AsyncGenerator[AIResponse, None]:
        """Stream chat responses"""
        async with self.client.stream(
            "POST",
            f"{self.BASE_URL}/chat/completions",
            json=payload,
        ) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    if line[6:].strip() == "[DONE]":
                        break
                    try:
                        data = json.loads(line[6:])
                        yield self._parse_stream_chunk(data, model)
                    except json.JSONDecodeError:
                        continue
    
    def _parse_response(self, data: Dict, model: str) -> AIResponse:
        choice = data.get("choices", [{}])[0]
        message = choice.get("message", {})
        
        return AIResponse(
            content=message.get("content", ""),
            model=model,
            provider=self.name,
            usage=data.get("usage", {}),
            finish_reason=choice.get("finish_reason"),
            tool_calls=message.get("tool_calls"),
            raw_response=data,
            cost_aud=0.0,
        )
    
    def _parse_stream_chunk(self, data: Dict, model: str) -> AIResponse:
        choice = data.get("choices", [{}])[0]
        delta = choice.get("delta", {})
        
        return AIResponse(
            content=delta.get("content", ""),
            model=model,
            provider=self.name,
            usage={},
            finish_reason=choice.get("finish_reason"),
            tool_calls=delta.get("tool_calls"),
            raw_response=data,
            cost_aud=0.0,
        )
    
    async def embed(
        self,
        texts: List[str],
        model: str = "text-embedding-nomic-embed-text-v1.5",
        **kwargs
    ) -> EmbeddingResponse:
        self._rate_limit()
        
        response = await self.client.post(
            f"{self.BASE_URL}/embeddings",
            json={"model": model, "input": texts},
        )
        response.raise_for_status()
        data = response.json()
        
        embeddings = [item["embedding"] for item in data.get("data", [])]
        
        return EmbeddingResponse(
            embeddings=embeddings,
            model=model,
            provider=self.name,
            usage=data.get("usage", {}),
            cost_aud=0.0,
        )
    
    async def list_models(self) -> List[Dict[str, Any]]:
        try:
            response = await self.client.get(f"{self.BASE_URL}/models")
            response.raise_for_status()
            data = response.json()
            
            models = []
            for m in data.get("data", []):
                models.append({
                    "id": m["id"],
                    "name": m.get("id", ""),
                    "owned_by": m.get("owned_by"),
                })
            
            return models
            
        except Exception as e:
            logger.error("LM Studio list_models error", error=str(e))
            return []
    
    async def health_check(self) -> bool:
        try:
            response = await self.client.get(f"{self.BASE_URL}/models")
            return response.status_code == 200
        except Exception:
            return False


# ============================================================
# AI PROVIDER REGISTRY
# ============================================================

class AIProviderRegistry:
    """Registry for managing AI providers"""
    
    def __init__(self):
        self._providers: Dict[str, AIProvider] = {}
        self._initialized = False
    
    def register(self, provider: AIProvider) -> None:
        self._providers[provider.name] = provider
        logger.info("AI Provider registered", name=provider.name, display_name=provider.display_name)
    
    def get(self, name: str) -> Optional[AIProvider]:
        return self._providers.get(name)
    
    def list(self) -> List[AIProvider]:
        return list(self._providers.values())
    
    def get_free_providers(self) -> List[AIProvider]:
        return [p for p in self._providers.values() if p.capabilities.is_free]
    
    def get_all_providers(self) -> List[AIProvider]:
        return list(self._providers.values())
    
    async def initialize_from_settings(self) -> None:
        if self._initialized:
            return
        
        # Local providers (always available)
        self.register(OllamaProvider())
        self.register(LMStudioProvider())
        
        # Cloud providers with API keys
        if settings.GEMINI_API_KEY:
            self.register(GeminiProvider())
        
        if settings.OPENROUTER_API_KEY:
            self.register(OpenRouterProvider())
        
        self._initialized = True
        logger.info("AI Provider registry initialized", count=len(self._providers))
    
    async def close_all(self) -> None:
        for provider in self._providers.values():
            await provider.close()
        self._providers.clear()
        self._initialized = False


# Global registry
ai_provider_registry = AIProviderRegistry()