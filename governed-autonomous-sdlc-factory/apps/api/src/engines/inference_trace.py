"""Inference Trace & Token Accounting.

Tracks every LLM inference call with full lineage:
- Prompt/response
- Model/provider used
- Token counts
- Cost
- Latency
- Reasoning metadata
- Derived artifacts
"""
from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from typing import Optional
from dataclasses import dataclass, field

from src.core.logging import get_logger

logger = get_logger("inference_trace")


@dataclass
class InferenceTraceRecord:
    """Complete record of a single inference call."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str = ""
    run_id: str = ""
    phase: str = ""
    provider: str = ""
    model: str = ""
    prompt_hash: str = ""
    response_hash: str = ""
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    cost_usd: float = 0.0
    latency_ms: float = 0.0
    success: bool = True
    error: Optional[str] = None
    fallback_used: bool = False
    fallback_from: Optional[str] = None
    reasoning: Optional[str] = None
    tool_calls: list = field(default_factory=list)
    derived_artifacts: list = field(default_factory=list)
    governance_impact: list = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass
class TokenAccount:
    """Token accounting for a session/run."""
    session_id: str = ""
    run_id: str = ""
    total_prompt_tokens: int = 0
    total_completion_tokens: int = 0
    total_tokens: int = 0
    total_cost_usd: float = 0.0
    total_calls: int = 0
    total_errors: int = 0
    total_latency_ms: float = 0.0
    models_used: dict = field(default_factory=dict)  # model -> {calls, tokens, cost}
    providers_used: dict = field(default_factory=dict)  # provider -> {calls, tokens, cost}
    phases: dict = field(default_factory=dict)  # phase -> {calls, tokens, cost}


class InferenceTracer:
    """Traces all inference calls for a run."""

    def __init__(self, run_id: str = "", session_id: str = ""):
        self.run_id = run_id
        self.session_id = session_id
        self._traces: list[InferenceTraceRecord] = []
        self._account = TokenAccount(run_id=run_id, session_id=session_id)

    def record(self, trace: InferenceTraceRecord) -> None:
        """Record an inference trace."""
        self._traces.append(trace)

        # Update account
        self._account.total_prompt_tokens += trace.prompt_tokens
        self._account.total_completion_tokens += trace.completion_tokens
        self._account.total_tokens += trace.total_tokens
        self._account.total_cost_usd += trace.cost_usd
        self._account.total_calls += 1
        self._account.total_latency_ms += trace.latency_ms
        if trace.success:
            pass
        else:
            self._account.total_errors += 1

        # Track models
        model_key = f"{trace.provider}:{trace.model}"
        if model_key not in self._account.models_used:
            self._account.models_used[model_key] = {"calls": 0, "tokens": 0, "cost": 0.0}
        self._account.models_used[model_key]["calls"] += 1
        self._account.models_used[model_key]["tokens"] += trace.total_tokens
        self._account.models_used[model_key]["cost"] += trace.cost_usd

        # Track providers
        if trace.provider not in self._account.providers_used:
            self._account.providers_used[trace.provider] = {"calls": 0, "tokens": 0, "cost": 0.0}
        self._account.providers_used[trace.provider]["calls"] += 1
        self._account.providers_used[trace.provider]["tokens"] += trace.total_tokens
        self._account.providers_used[trace.provider]["cost"] += trace.cost_usd

        # Track phases
        if trace.phase not in self._account.phases:
            self._account.phases[trace.phase] = {"calls": 0, "tokens": 0, "cost": 0.0}
        self._account.phases[trace.phase]["calls"] += 1
        self._account.phases[trace.phase]["tokens"] += trace.total_tokens
        self._account.phases[trace.phase]["cost"] += trace.cost_usd

    def get_traces(self) -> list[InferenceTraceRecord]:
        return self._traces

    def get_account(self) -> TokenAccount:
        return self._account

    def get_summary(self) -> dict:
        return {
            "run_id": self.run_id,
            "session_id": self.session_id,
            "total_traces": len(self._traces),
            "total_tokens": self._account.total_tokens,
            "total_cost_usd": round(self._account.total_cost_usd, 4),
            "total_calls": self._account.total_calls,
            "total_errors": self._account.total_errors,
            "avg_latency_ms": round(self._account.total_latency_ms / max(self._account.total_calls, 1), 1),
            "models_used": self._account.models_used,
            "providers_used": self._account.providers_used,
            "phases": self._account.phases,
        }
