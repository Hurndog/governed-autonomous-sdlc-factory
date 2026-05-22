"""Ollama provider adapter for the Model Router.

Supports local models via Ollama's API.
"""
from __future__ import annotations

import time
from typing import Optional

import httpx

from src.core.logging import get_logger
from src.engines.model_providers import BaseProvider, InferenceResult, ProviderType, ModelCapabilities

logger = get_logger("model_router.ollama")


class OllamaProvider(BaseProvider):
    """Ollama adapter — local models via Ollama API."""

    provider_type = ProviderType.OLLAMA

    def __init__(self, base_url: str = "http://localhost:11434", **kwargs):
        super().__init__(api_key="", base_url=base_url, **kwargs)

    async def complete(
        self,
        messages: list[dict],
        model: str = "gpt-oss:20b",
        temperature: float = 0.7,
        max_tokens: int = 4096,
        stream: bool = False,
        response_format: Optional[dict] = None,
        tools: Optional[list] = None,
    ) -> InferenceResult:
        start = time.monotonic()
        client = await self._get_client()

        # Convert messages to Ollama prompt format
        prompt = self._messages_to_prompt(messages)

        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            },
        }

        # Ollama doesn't support response_format directly, but we can instruct via prompt
        if response_format and response_format.get("type") == "json_object":
            prompt += "\n\nIMPORTANT: Output ONLY valid JSON. No markdown, no explanations.\n"
            payload["prompt"] = prompt

        try:
            resp = await client.post("/api/generate", json=payload, timeout=300)
            resp.raise_for_status()
            data = resp.json()

            response_text = data.get("response", "")
            latency = (time.monotonic() - start) * 1000

            # Ollama provides token counts
            prompt_tokens = data.get("prompt_eval_count", 0)
            completion_tokens = data.get("eval_count", 0)

            return InferenceResult(
                provider=self.provider_type.value,
                model=model,
                prompt=prompt[:500],
                response=response_text,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=prompt_tokens + completion_tokens,
                latency_ms=latency,
                raw_response=data,
            )
        except Exception as e:
            latency = (time.monotonic() - start) * 1000
            logger.error(f"Ollama inference failed: {e}")
            return InferenceResult(
                provider=self.provider_type.value,
                model=model,
                prompt=prompt[:500],
                response="",
                latency_ms=latency,
                success=False,
                error=str(e),
            )

    def _messages_to_prompt(self, messages: list[dict]) -> str:
        """Convert OpenAI-style messages to a single prompt string."""
        parts = []
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            if role == "system":
                parts.append(f"System: {content}")
            elif role == "user":
                parts.append(f"User: {content}")
            elif role == "assistant":
                parts.append(f"Assistant: {content}")
        return "\n\n".join(parts) + "\n\nAssistant:"

    async def health_check(self) -> dict:
        """Check if Ollama is reachable and return status."""
        start = time.monotonic()
        try:
            client = await self._get_client()
            resp = await client.get("/api/version", timeout=10)
            latency = (time.monotonic() - start) * 1000
            if resp.status_code == 200:
                data = resp.json()
                return {
                    "status": "available",
                    "version": data.get("version", "unknown"),
                    "latency_ms": round(latency, 2),
                    "provider": "ollama",
                }
            return {
                "status": "unhealthy",
                "error": f"HTTP {resp.status_code}",
                "latency_ms": round(latency, 2),
                "provider": "ollama",
            }
        except Exception as e:
            latency = (time.monotonic() - start) * 1000
            return {
                "status": "unavailable",
                "error": str(e),
                "latency_ms": round(latency, 2),
                "provider": "ollama",
            }

    async def list_available_models(self) -> list[dict]:
        """List models available through Ollama."""
        try:
            client = await self._get_client()
            resp = await client.get("/api/tags", timeout=10)
            resp.raise_for_status()
            data = resp.json()
            models = data.get("models", [])
            return [
                {
                    "model_id": m.get("name", ""),
                    "size_bytes": m.get("size", 0),
                    "digest": m.get("digest", ""),
                    "modified_at": m.get("modified_at", ""),
                }
                for m in models
            ]
        except Exception as e:
            logger.error(f"Ollama list_models failed: {e}")
            return []
