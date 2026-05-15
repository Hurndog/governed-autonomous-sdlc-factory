"""Model Provider Adapters for the Cognitive Cortex.

Provides unified interface for LLM inference across:
- LM Studio (local, OpenAI-compatible)
- OpenAI (GPT-4, GPT-4o, etc.)
- Anthropic (Claude)
- Ollama (local)
- OpenRouter (aggregator)

Each adapter implements the same interface:
    async complete(messages, model, **kwargs) -> InferenceResult
"""
from __future__ import annotations

import asyncio
import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Optional
from enum import Enum

import httpx

from src.core.logging import get_logger

logger = get_logger("model_router.providers")


class ProviderType(str, Enum):
    LM_STUDIO = "lm_studio"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    OLLAMA = "ollama"
    OPENROUTER = "openrouter"


@dataclass
class InferenceResult:
    """Result of a single inference call."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    provider: str = ""
    model: str = ""
    prompt: str = ""
    response: str = ""
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    latency_ms: float = 0.0
    cost_usd: float = 0.0
    reasoning: Optional[str] = None
    tool_calls: list = field(default_factory=list)
    raw_response: dict = field(default_factory=dict)
    success: bool = True
    error: Optional[str] = None
    created_at: str = field(default_factory=lambda: time.strftime("%Y-%m-%dT%H:%M:%S%z"))


@dataclass
class ModelCapabilities:
    """Capabilities of a specific model."""
    model_id: str
    provider: str
    context_length: int = 8192
    supports_streaming: bool = True
    supports_structured_output: bool = False
    supports_vision: bool = False
    supports_function_calling: bool = False
    supports_reasoning: bool = False
    cost_per_1k_prompt_tokens: float = 0.0
    cost_per_1k_completion_tokens: float = 0.0
    modality: str = "text"
    latency_tier: str = "medium"  # low, medium, high


class BaseProvider:
    """Base class for all model providers."""

    provider_type: ProviderType = ProviderType.OPENAI

    def __init__(self, api_key: str = "", base_url: str = "", timeout: float = 120.0):
        self.api_key = api_key
        self.base_url = base_url
        self.timeout = timeout
        self._client: Optional[httpx.AsyncClient] = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=self.timeout,
                headers=self._default_headers(),
            )
        return self._client

    def _default_headers(self) -> dict:
        return {"Content-Type": "application/json"}

    async def complete(
        self,
        messages: list[dict],
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        stream: bool = False,
        response_format: Optional[dict] = None,
        tools: Optional[list] = None,
    ) -> InferenceResult:
        raise NotImplementedError

    async def close(self):
        if self._client and not self._client.is_closed:
            await self._client.aclose()

    def _build_result(
        self,
        model: str,
        prompt: str,
        response: str,
        prompt_tokens: int = 0,
        completion_tokens: int = 0,
        latency_ms: float = 0.0,
        raw: dict = None,
        success: bool = True,
        error: str = None,
    ) -> InferenceResult:
        total = prompt_tokens + completion_tokens
        return InferenceResult(
            provider=self.provider_type.value,
            model=model,
            prompt=prompt[:500],
            response=response,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total,
            latency_ms=latency_ms,
            raw_response=raw or {},
            success=success,
            error=error,
        )


class LMStudioProvider(BaseProvider):
    """LM Studio adapter — local models via OpenAI-compatible API."""

    provider_type = ProviderType.LM_STUDIO

    def __init__(self, base_url: str = "http://localhost:1234/v1", api_key: str = "lm-studio", **kwargs):
        super().__init__(api_key=api_key, base_url=base_url, **kwargs)

    async def complete(
        self,
        messages: list[dict],
        model: str = "local-model",
        temperature: float = 0.7,
        max_tokens: int = 4096,
        stream: bool = False,
        response_format: Optional[dict] = None,
        tools: Optional[list] = None,
    ) -> InferenceResult:
        start = time.monotonic()
        client = await self._get_client()

        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": stream,
        }
        if response_format:
            payload["response_format"] = response_format
        if tools:
            payload["tools"] = tools

        try:
            resp = await client.post("/chat/completions", json=payload)
            resp.raise_for_status()
            data = resp.json()

            choice = data.get("choices", [{}])[0]
            message = choice.get("message", {})
            response_text = message.get("content", "")
            reasoning = message.get("reasoning_content") or message.get("reasoning")

            usage = data.get("usage", {})
            latency = (time.monotonic() - start) * 1000

            prompt_text = " ".join(m.get("content", "")[:200] for m in messages)

            return self._build_result(
                model=model,
                prompt=prompt_text,
                response=response_text,
                prompt_tokens=usage.get("prompt_tokens", 0),
                completion_tokens=usage.get("completion_tokens", 0),
                latency_ms=latency,
                raw=data,
            )
        except Exception as e:
            latency = (time.monotonic() - start) * 1000
            logger.error(f"LM Studio inference failed: {e}")
            return self._build_result(
                model=model,
                prompt="",
                response="",
                latency_ms=latency,
                success=False,
                error=str(e),
            )


class OpenAIProvider(BaseProvider):
    """OpenAI adapter — GPT-4, GPT-4o, GPT-4o-mini, etc."""

    provider_type = ProviderType.OPENAI

    def __init__(self, api_key: str, base_url: str = "https://api.openai.com/v1", **kwargs):
        super().__init__(api_key=api_key, base_url=base_url, **kwargs)

    def _default_headers(self) -> dict:
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

    async def complete(
        self,
        messages: list[dict],
        model: str = "gpt-4o",
        temperature: float = 0.7,
        max_tokens: int = 4096,
        stream: bool = False,
        response_format: Optional[dict] = None,
        tools: Optional[list] = None,
    ) -> InferenceResult:
        start = time.monotonic()
        client = await self._get_client()

        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": stream,
        }
        if response_format:
            payload["response_format"] = response_format
        if tools:
            payload["tools"] = tools

        try:
            resp = await client.post("/chat/completions", json=payload)
            resp.raise_for_status()
            data = resp.json()

            choice = data.get("choices", [{}])[0]
            message = choice.get("message", {})
            response_text = message.get("content", "")

            usage = data.get("usage", {})
            latency = (time.monotonic() - start) * 1000

            # Calculate cost based on model
            prompt_tokens = usage.get("prompt_tokens", 0)
            completion_tokens = usage.get("completion_tokens", 0)
            cost = self._calculate_cost(model, prompt_tokens, completion_tokens)

            prompt_text = " ".join(m.get("content", "")[:200] for m in messages)

            return InferenceResult(
                provider=self.provider_type.value,
                model=model,
                prompt=prompt_text,
                response=response_text,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=prompt_tokens + completion_tokens,
                latency_ms=latency,
                cost_usd=cost,
                raw_response=data,
            )
        except Exception as e:
            latency = (time.monotonic() - start) * 1000
            logger.error(f"OpenAI inference failed: {e}")
            return self._build_result(
                model=model, prompt="", response="", latency_ms=latency, success=False, error=str(e)
            )

    def _calculate_cost(self, model: str, prompt_tokens: int, completion_tokens: int) -> float:
        """Calculate cost in USD based on model pricing."""
        pricing = {
            "gpt-4o": (0.0025, 0.01),
            "gpt-4o-mini": (0.00015, 0.0006),
            "gpt-4-turbo": (0.01, 0.03),
            "gpt-4": (0.03, 0.06),
            "gpt-3.5-turbo": (0.0005, 0.0015),
        }
        prompt_cost, completion_cost = pricing.get(model, (0.0025, 0.01))
        return (prompt_tokens / 1000 * prompt_cost) + (completion_tokens / 1000 * completion_cost)


class AnthropicProvider(BaseProvider):
    """Anthropic adapter — Claude 3.5 Sonnet, Claude 3 Opus, etc."""

    provider_type = ProviderType.ANTHROPIC

    def __init__(self, api_key: str, base_url: str = "https://api.anthropic.com", **kwargs):
        super().__init__(api_key=api_key, base_url=base_url, **kwargs)

    def _default_headers(self) -> dict:
        return {
            "Content-Type": "application/json",
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "anthropic-dangerous-direct-browser-access": "true",
        }

    async def complete(
        self,
        messages: list[dict],
        model: str = "claude-3-5-sonnet-20241022",
        temperature: float = 0.7,
        max_tokens: int = 4096,
        stream: bool = False,
        response_format: Optional[dict] = None,
        tools: Optional[list] = None,
    ) -> InferenceResult:
        start = time.monotonic()
        client = await self._get_client()

        # Convert OpenAI-style messages to Anthropic format
        system_message = ""
        anthropic_messages = []
        for msg in messages:
            if msg.get("role") == "system":
                system_message = msg.get("content", "")
            else:
                anthropic_messages.append({
                    "role": msg["role"],
                    "content": msg.get("content", ""),
                })

        payload = {
            "model": model,
            "messages": anthropic_messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }
        if system_message:
            payload["system"] = system_message
        if tools:
            payload["tools"] = tools

        try:
            resp = await client.post("/v1/messages", json=payload)
            resp.raise_for_status()
            data = resp.json()

            # Extract response text
            content_blocks = data.get("content", [])
            response_text = "".join(
                block.get("text", "") for block in content_blocks if block.get("type") == "text"
            )

            usage = data.get("usage", {})
            latency = (time.monotonic() - start) * 1000

            prompt_tokens = usage.get("input_tokens", 0)
            completion_tokens = usage.get("output_tokens", 0)
            cost = self._calculate_cost(model, prompt_tokens, completion_tokens)

            prompt_text = " ".join(m.get("content", "")[:200] for m in messages)

            return InferenceResult(
                provider=self.provider_type.value,
                model=model,
                prompt=prompt_text,
                response=response_text,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=prompt_tokens + completion_tokens,
                latency_ms=latency,
                cost_usd=cost,
                raw_response=data,
            )
        except Exception as e:
            latency = (time.monotonic() - start) * 1000
            logger.error(f"Anthropic inference failed: {e}")
            return self._build_result(
                model=model, prompt="", response="", latency_ms=latency, success=False, error=str(e)
            )

    def _calculate_cost(self, model: str, prompt_tokens: int, completion_tokens: int) -> float:
        pricing = {
            "claude-3-5-sonnet-20241022": (0.003, 0.015),
            "claude-3-5-sonnet-20240620": (0.003, 0.015),
            "claude-3-opus-20240229": (0.015, 0.075),
            "claude-3-haiku-20240307": (0.00025, 0.00125),
        }
        prompt_cost, completion_cost = pricing.get(model, (0.003, 0.015))
        return (prompt_tokens / 1000 * prompt_cost) + (completion_tokens / 1000 * completion_cost)
