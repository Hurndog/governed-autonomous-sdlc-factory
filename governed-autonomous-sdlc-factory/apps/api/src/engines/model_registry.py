"""Model Registry — tracks available models and their capabilities.

Maintains a registry of all configured models across providers,
their capabilities, costs, and routing preferences.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime, timezone

from src.core.logging import get_logger
from src.engines.model_providers import ModelCapabilities, ProviderType

logger = get_logger("model_router.registry")


@dataclass
class ModelEntry:
    """A registered model."""
    model_id: str
    provider: str
    display_name: str
    capabilities: ModelCapabilities
    is_available: bool = True
    is_default: bool = False
    priority: int = 0  # higher = preferred
    config: dict = field(default_factory=dict)
    last_used: Optional[str] = None
    total_calls: int = 0
    total_tokens: int = 0
    total_cost_usd: float = 0.0
    avg_latency_ms: float = 0.0
    error_count: int = 0


class ModelRegistry:
    """Central registry of all available models."""

    def __init__(self):
        self._models: dict[str, ModelEntry] = {}
        self._default_model: Optional[str] = None

    def register(self, entry: ModelEntry) -> None:
        """Register a model."""
        key = f"{entry.provider}:{entry.model_id}"
        self._models[key] = entry
        if entry.is_default and not self._default_model:
            self._default_model = key
        logger.info(f"Registered model: {key}")

    def unregister(self, provider: str, model_id: str) -> None:
        """Unregister a model."""
        key = f"{provider}:{model_id}"
        if key in self._models:
            del self._models[key]
            if self._default_model == key:
                self._default_model = None

    def get(self, provider: str, model_id: str) -> Optional[ModelEntry]:
        """Get a model entry."""
        return self._models.get(f"{provider}:{model_id}")

    def get_default(self) -> Optional[ModelEntry]:
        """Get the default model (must be available)."""
        if self._default_model:
            entry = self._models.get(self._default_model)
            if entry and entry.is_available:
                return entry
        # Return first available
        for entry in self._models.values():
            if entry.is_available:
                return entry
        return None

    def get_configured_default(self) -> Optional[ModelEntry]:
        """Get the configured default model (even if unavailable)."""
        if self._default_model:
            return self._models.get(self._default_model)
        # Return first configured model
        for entry in self._models.values():
            return entry
        return None

    def get_availability_summary(self) -> dict:
        """Get summary of model availability."""
        total = len(self._models)
        available = sum(1 for e in self._models.values() if e.is_available)
        unavailable = total - available
        return {
            "total": total,
            "available": available,
            "unavailable": unavailable,
            "models": {
                key: {
                    "provider": e.provider,
                    "model_id": e.model_id,
                    "display_name": e.display_name,
                    "is_available": e.is_available,
                    "is_default": e.is_default,
                    "priority": e.priority,
                }
                for key, e in self._models.items()
            },
        }

    def list_models(
        self,
        provider: Optional[str] = None,
        available_only: bool = False,
        min_context: int = 0,
    ) -> list[ModelEntry]:
        """List registered models with optional filtering.

        Args:
            provider: Filter by provider name
            available_only: If True, only return available models.
                          If False, return all configured models.
            min_context: Minimum context length filter
        """
        results = []
        for entry in self._models.values():
            if available_only and not entry.is_available:
                continue
            if provider and entry.provider != provider:
                continue
            if min_context and entry.capabilities.context_length < min_context:
                continue
            results.append(entry)
        return sorted(results, key=lambda e: (-e.priority, e.display_name))

    def update_stats(self, provider: str, model_id: str, tokens: int, cost: float, latency_ms: float, error: bool = False) -> None:
        """Update usage statistics for a model."""
        entry = self.get(provider, model_id)
        if not entry:
            return
        entry.total_calls += 1
        entry.total_tokens += tokens
        entry.total_cost_usd += cost
        entry.last_used = datetime.now(timezone.utc).isoformat()
        # Rolling average latency
        entry.avg_latency_ms = (entry.avg_latency_ms * (entry.total_calls - 1) + latency_ms) / entry.total_calls
        if error:
            entry.error_count += 1

    def get_stats(self) -> dict:
        """Get aggregate statistics."""
        total_calls = sum(e.total_calls for e in self._models.values())
        total_tokens = sum(e.total_tokens for e in self._models.values())
        total_cost = sum(e.total_cost_usd for e in self._models.values())
        total_errors = sum(e.error_count for e in self._models.values())
        return {
            "total_models": len(self._models),
            "available_models": sum(1 for e in self._models.values() if e.is_available),
            "total_calls": total_calls,
            "total_tokens": total_tokens,
            "total_cost_usd": round(total_cost, 4),
            "total_errors": total_errors,
            "models": {
                key: {
                    "calls": e.total_calls,
                    "tokens": e.total_tokens,
                    "cost_usd": round(e.total_cost_usd, 4),
                    "avg_latency_ms": round(e.avg_latency_ms, 1),
                    "errors": e.error_count,
                }
                for key, e in self._models.items()
            },
        }

    def load_defaults(self) -> None:
        """Load default model configurations."""
        defaults = [
            ModelEntry(
                model_id="local-model",
                provider=ProviderType.LM_STUDIO.value,
                display_name="LM Studio (Local)",
                capabilities=ModelCapabilities(
                    model_id="local-model",
                    provider=ProviderType.LM_STUDIO.value,
                    context_length=32768,
                    supports_streaming=True,
                    supports_structured_output=True,
                    cost_per_1k_prompt_tokens=0.0,
                    cost_per_1k_completion_tokens=0.0,
                    latency_tier="low",
                ),
                is_available=False,  # Will be detected at runtime
                priority=10,
                is_default=True,  # First registered model becomes default
            ),
            ModelEntry(
                model_id="gpt-4o-mini",
                provider=ProviderType.OPENAI.value,
                display_name="GPT-4o Mini",
                capabilities=ModelCapabilities(
                    model_id="gpt-4o-mini",
                    provider=ProviderType.OPENAI.value,
                    context_length=128000,
                    supports_streaming=True,
                    supports_structured_output=True,
                    supports_function_calling=True,
                    cost_per_1k_prompt_tokens=0.00015,
                    cost_per_1k_completion_tokens=0.0006,
                    latency_tier="low",
                ),
                is_available=False,
                priority=20,
            ),
            ModelEntry(
                model_id="gpt-4o",
                provider=ProviderType.OPENAI.value,
                display_name="GPT-4o",
                capabilities=ModelCapabilities(
                    model_id="gpt-4o",
                    provider=ProviderType.OPENAI.value,
                    context_length=128000,
                    supports_streaming=True,
                    supports_structured_output=True,
                    supports_function_calling=True,
                    supports_vision=True,
                    cost_per_1k_prompt_tokens=0.0025,
                    cost_per_1k_completion_tokens=0.01,
                    latency_tier="medium",
                ),
                is_available=False,
                priority=30,
            ),
            ModelEntry(
                model_id="claude-3-5-sonnet-20241022",
                provider=ProviderType.ANTHROPIC.value,
                display_name="Claude 3.5 Sonnet",
                capabilities=ModelCapabilities(
                    model_id="claude-3-5-sonnet-20241022",
                    provider=ProviderType.ANTHROPIC.value,
                    context_length=200000,
                    supports_streaming=True,
                    supports_structured_output=True,
                    supports_function_calling=True,
                    supports_vision=True,
                    cost_per_1k_prompt_tokens=0.003,
                    cost_per_1k_completion_tokens=0.015,
                    latency_tier="medium",
                ),
                is_available=False,
                priority=25,
            ),
        ]
        for entry in defaults:
            self.register(entry)
        logger.info(f"Loaded {len(defaults)} default model configurations")
