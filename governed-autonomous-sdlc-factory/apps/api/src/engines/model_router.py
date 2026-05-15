"""Model Router — unified LLM inference orchestration.

Routes inference requests to appropriate providers based on:
- Model availability
- Capability requirements
- Cost optimization
- Fallback policies
- Load balancing

This is the central AI execution engine for the Cognitive Cortex.
All AI-driven generation flows through this router.
"""
from __future__ import annotations

import asyncio
import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Optional
from datetime import datetime, timezone

from src.core.logging import get_logger
from src.core.config import settings
from src.engines.model_providers import (
    BaseProvider, LMStudioProvider, OpenAIProvider, AnthropicProvider,
    InferenceResult, ProviderType,
)
from src.engines.model_registry import ModelRegistry, ModelEntry

logger = get_logger("model_router")


@dataclass
class RoutingPolicy:
    """Policy for model selection."""
    prefer_local: bool = True
    max_cost_per_request: float = 0.10
    prefer_low_latency: bool = True
    require_structured_output: bool = False
    require_vision: bool = False
    require_function_calling: bool = False
    min_context_length: int = 8192
    fallback_enabled: bool = True
    max_retries: int = 3


@dataclass
class InferenceTrace:
    """Complete trace of an inference request."""
    trace_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str = ""
    run_id: str = ""
    phase: str = ""
    provider: str = ""
    model: str = ""
    prompt: str = ""
    response: str = ""
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    cost_usd: float = 0.0
    latency_ms: float = 0.0
    success: bool = True
    error: Optional[str] = None
    fallback_used: bool = False
    fallback_from: Optional[str] = None
    routing_policy: str = ""
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class ModelRouter:
    """Central model router for all AI inference.

    Usage:
        router = ModelRouter()
        await router.initialize()
        result = router.complete(messages=[{"role": "user", "content": "Hello"}])
    """

    def __init__(self):
        self.registry = ModelRegistry()
        self._providers: dict[str, BaseProvider] = {}
        self._policy = RoutingPolicy()
        self._initialized = False
        self._traces: list[InferenceTrace] = []

    async def initialize(self) -> None:
        """Initialize providers from configuration."""
        self.registry.load_defaults()

        # Initialize LM Studio (local, always try first)
        lm_studio = LMStudioProvider(
            base_url=settings.lm_studio_url,
            api_key="lm-studio",
        )
        self._providers[ProviderType.LM_STUDIO.value] = lm_studio

        # Initialize OpenAI if API key available
        if settings.openai_api_key:
            openai = OpenAIProvider(api_key=settings.openai_api_key)
            self._providers[ProviderType.OPENAI.value] = openai
            # Mark models as available
            for key, entry in self.registry._models.items():
                if entry.provider == ProviderType.OPENAI.value:
                    entry.is_available = True
            logger.info("OpenAI provider initialized")

        # Initialize Anthropic if API key available
        if settings.anthropic_api_key:
            anthropic = AnthropicProvider(api_key=settings.anthropic_api_key)
            self._providers[ProviderType.ANTHROPIC.value] = anthropic
            for key, entry in self.registry._models.items():
                if entry.provider == ProviderType.ANTHROPIC.value:
                    entry.is_available = True
            logger.info("Anthropic provider initialized")

        # Probe LM Studio availability
        try:
            result = await lm_studio.complete(
                messages=[{"role": "user", "content": "ping"}],
                model="local-model",
                max_tokens=10,
            )
            if result.success:
                for key, entry in self.registry._models.items():
                    if entry.provider == ProviderType.LM_STUDIO.value:
                        entry.is_available = True
                logger.info("LM Studio is available")
            else:
                logger.info("LM Studio probe failed, will use remote providers")
        except Exception:
            logger.info("LM Studio not reachable, will use remote providers")

        self._initialized = True
        available = sum(1 for e in self.registry._models.values() if e.is_available)
        logger.info(f"ModelRouter initialized: {available} available models")

    async def complete(
        self,
        messages: list[dict],
        model: Optional[str] = None,
        provider: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        response_format: Optional[dict] = None,
        tools: Optional[list] = None,
        policy: Optional[RoutingPolicy] = None,
        session_id: str = "",
        run_id: str = "",
        phase: str = "",
    ) -> InferenceResult:
        """Execute an inference request.

        Routes to the best available model based on policy.
        Falls back to alternative providers on failure.
        """
        if not self._initialized:
            await self.initialize()

        policy = policy or self._policy
        trace = InferenceTrace(
            session_id=session_id,
            run_id=run_id,
            phase=phase,
        )

        # Select model
        model_entry, selected_provider = self._select_model(
            model=model,
            provider=provider,
            policy=policy,
        )

        if not model_entry or not selected_provider:
            error_msg = "No available model found for request"
            logger.error(error_msg)
            trace.success = False
            trace.error = error_msg
            self._traces.append(trace)
            return InferenceResult(success=False, error=error_msg)

        # Execute with fallback
        result = await self._execute_with_fallback(
            messages=messages,
            model_entry=model_entry,
            provider=selected_provider,
            temperature=temperature,
            max_tokens=max_tokens,
            response_format=response_format,
            tools=tools,
            policy=policy,
            trace=trace,
        )

        # Update trace
        trace.provider = result.provider
        trace.model = result.model
        trace.prompt = result.prompt[:500]
        trace.response = result.response[:1000]
        trace.prompt_tokens = result.prompt_tokens
        trace.completion_tokens = result.completion_tokens
        trace.total_tokens = result.total_tokens
        trace.cost_usd = result.cost_usd
        trace.latency_ms = result.latency_ms
        trace.success = result.success
        trace.error = result.error
        self._traces.append(trace)

        # Update registry stats
        self.registry.update_stats(
            provider=result.provider,
            model_id=result.model,
            tokens=result.total_tokens,
            cost=result.cost_usd,
            latency_ms=result.latency_ms,
            error=not result.success,
        )

        return result

    def _select_model(
        self,
        model: Optional[str] = None,
        provider: Optional[str] = None,
        policy: RoutingPolicy = None,
    ) -> tuple[Optional[ModelEntry], Optional[BaseProvider]]:
        """Select the best model for the request."""

        # Explicit model/provider selection
        if model and provider:
            entry = self.registry.get(provider, model)
            prov = self._providers.get(provider)
            if entry and prov and entry.is_available:
                return entry, prov

        # Policy-based selection
        candidates = self.registry.list_models(available_only=True)

        # Filter by requirements
        if policy:
            if policy.require_structured_output:
                candidates = [c for c in candidates if c.capabilities.supports_structured_output]
            if policy.require_vision:
                candidates = [c for c in candidates if c.capabilities.supports_vision]
            if policy.require_function_calling:
                candidates = [c for c in candidates if c.capabilities.supports_function_calling]
            if policy.min_context_length:
                candidates = [c for c in candidates if c.capabilities.context_length >= policy.min_context_length]

        if not candidates:
            return None, None

        # Prefer local models if policy says so
        if policy and policy.prefer_local:
            local = [c for c in candidates if c.provider == ProviderType.LM_STUDIO.value]
            if local:
                candidates = local

        # Select highest priority
        selected = candidates[0]
        provider_instance = self._providers.get(selected.provider)

        return selected, provider_instance

    async def _execute_with_fallback(
        self,
        messages: list[dict],
        model_entry: ModelEntry,
        provider: BaseProvider,
        temperature: float,
        max_tokens: int,
        response_format: Optional[dict],
        tools: Optional[list],
        policy: RoutingPolicy,
        trace: InferenceTrace,
    ) -> InferenceResult:
        """Execute inference with fallback on failure."""
        last_error = None

        for attempt in range(policy.max_retries):
            try:
                result = await provider.complete(
                    messages=messages,
                    model=model_entry.model_id,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    response_format=response_format,
                    tools=tools,
                )

                if result.success:
                    if attempt > 0:
                        trace.fallback_used = True
                        trace.fallback_from = f"{model_entry.provider}:{model_entry.model_id}"
                    return result

                last_error = result.error
                logger.warning(f"Attempt {attempt + 1} failed: {last_error}")

            except Exception as e:
                last_error = str(e)
                logger.warning(f"Attempt {attempt + 1} exception: {e}")

            # Try fallback model
            if policy.fallback_enabled and attempt < policy.max_retries - 1:
                fallback_entry, fallback_provider = self._get_fallback(model_entry)
                if fallback_entry and fallback_provider:
                    model_entry = fallback_entry
                    provider = fallback_provider
                    logger.info(f"Falling back to {fallback_entry.provider}:{fallback_entry.model_id}")

        return InferenceResult(
            success=False,
            error=f"All {policy.max_retries} attempts failed. Last error: {last_error}",
        )

    def _get_fallback(self, current: ModelEntry) -> tuple[Optional[ModelEntry], Optional[BaseProvider]]:
        """Get a fallback model different from current."""
        candidates = self.registry.list_models(available_only=True)
        for c in candidates:
            if c.provider != current.provider or c.model_id != current.model_id:
                prov = self._providers.get(c.provider)
                if prov:
                    return c, prov
        return None, None

    def get_traces(self, limit: int = 100) -> list[InferenceTrace]:
        """Get recent inference traces."""
        return self._traces[-limit:]

    def get_stats(self) -> dict:
        """Get router statistics."""
        return {
            "initialized": self._initialized,
            "providers": list(self._providers.keys()),
            "registry": self.registry.get_stats(),
            "total_traces": len(self._traces),
        }

    async def close(self) -> None:
        """Close all provider connections."""
        for provider in self._providers.values():
            await provider.close()


# Global router instance
_router: Optional[ModelRouter] = None


async def get_router() -> ModelRouter:
    """Get or create the global model router."""
    global _router
    if _router is None:
        _router = ModelRouter()
        await _router.initialize()
    return _router


async def complete(
    messages: list[dict],
    model: Optional[str] = None,
    provider: Optional[str] = None,
    **kwargs,
) -> InferenceResult:
    """Convenience function for inference."""
    router = await get_router()
    return await router.complete(messages, model=model, provider=provider, **kwargs)
