"""
v0.5 Multi-Model Cognitive Governance — Capability Registry, Model Router, Arbitration Engine.

New classes that extend (not replace) the existing model_providers.py.
"""

from __future__ import annotations

import asyncio
import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Optional, Dict, List
from enum import Enum

from src.core.logging import get_logger

logger = get_logger("model_router.v05")


# ── Enums ───────────────────────────────────────────────────────────────────

class SovereigntyLevel(str, Enum):
    FRONTIER_ONLY = "frontier_only"
    SOVEREIGN_PREFERRED = "sovereign_preferred"
    SOVEREIGN_REQUIRED = "sovereign_required"
    LOCAL_ONLY = "local_only"
    HYBRID = "hybrid"


class TaskType(str, Enum):
    CODE_GENERATION = "code_generation"
    ARCHITECTURE_REASONING = "architecture_reasoning"
    GOVERNANCE_ANALYSIS = "governance_analysis"
    REPLAY_ANALYSIS = "replay_analysis"
    SEMANTIC_EVALUATION = "semantic_evaluation"
    SPECIFICATION_GENERATION = "specification_generation"
    MUTATION_REASONING = "mutation_reasoning"
    DRIFT_ANALYSIS = "drift_analysis"
    OPERATOR_EXPLANATION = "operator_explanation"
    MEMORY_CLASSIFICATION = "memory_classification"


# ── Model Capabilities ─────────────────────────────────────────────────────

@dataclass
class ModelCapability:
    provider: str
    model: str
    coding_quality: float = 0.5
    reasoning_quality: float = 0.5
    governance_reliability: float = 0.5
    hallucination_risk: float = 0.5
    latency_score: float = 0.5
    cost_score: float = 0.5
    context_window: int = 8192
    structured_output_reliability: float = 0.5
    replay_stability: float = 0.5
    semantic_consistency: float = 0.5
    sovereignty_level: SovereigntyLevel = SovereigntyLevel.HYBRID
    availability: float = 1.0
    operator_trust: float = 0.5
    historical_failure_rate: float = 0.0
    supports_streaming: bool = True
    supports_structured_output: bool = False
    supports_vision: bool = False
    supports_function_calling: bool = False
    updated_at: str = field(default_factory=lambda: time.strftime("%Y-%m-%dT%H:%M:%S%z"))


# ── Capability Registry ────────────────────────────────────────────────────

class ModelCapabilityRegistry:
    def __init__(self):
        self._capabilities: Dict[str, ModelCapability] = {}
        self._load_defaults()

    def _load_defaults(self):
        defaults = [
            ModelCapability("ollama", "phi3:mini", coding_quality=0.6, reasoning_quality=0.5, governance_reliability=0.4, hallucination_risk=0.4, latency_score=0.2, cost_score=0.0, context_window=4096, structured_output_reliability=0.4, replay_stability=0.5, semantic_consistency=0.5, sovereignty_level=SovereigntyLevel.LOCAL_ONLY, operator_trust=0.5),
            ModelCapability("ollama", "qwen2.5:1.5b", coding_quality=0.7, reasoning_quality=0.6, governance_reliability=0.5, hallucination_risk=0.35, latency_score=0.2, cost_score=0.0, context_window=32768, structured_output_reliability=0.6, replay_stability=0.6, semantic_consistency=0.6, sovereignty_level=SovereigntyLevel.LOCAL_ONLY, operator_trust=0.6),
            ModelCapability("ollama", "gpt-oss:20b", coding_quality=0.8, reasoning_quality=0.75, governance_reliability=0.6, hallucination_risk=0.3, latency_score=0.3, cost_score=0.0, context_window=131072, structured_output_reliability=0.7, replay_stability=0.7, semantic_consistency=0.7, sovereignty_level=SovereigntyLevel.LOCAL_ONLY, operator_trust=0.7),
            ModelCapability("openai", "gpt-4o", coding_quality=0.9, reasoning_quality=0.9, governance_reliability=0.8, hallucination_risk=0.2, latency_score=0.4, cost_score=0.7, context_window=128000, structured_output_reliability=0.9, replay_stability=0.85, semantic_consistency=0.85, sovereignty_level=SovereigntyLevel.FRONTIER_ONLY, operator_trust=0.8),
            ModelCapability("openai", "gpt-4o-mini", coding_quality=0.8, reasoning_quality=0.75, governance_reliability=0.7, hallucination_risk=0.25, latency_score=0.3, cost_score=0.3, context_window=128000, structured_output_reliability=0.8, replay_stability=0.8, semantic_consistency=0.8, sovereignty_level=SovereigntyLevel.FRONTIER_ONLY, operator_trust=0.75),
            ModelCapability("anthropic", "claude-3-5-sonnet-20241022", coding_quality=0.9, reasoning_quality=0.9, governance_reliability=0.85, hallucination_risk=0.15, latency_score=0.4, cost_score=0.6, context_window=200000, structured_output_reliability=0.85, replay_stability=0.9, semantic_consistency=0.9, sovereignty_level=SovereigntyLevel.FRONTIER_ONLY, operator_trust=0.85),
            ModelCapability("openrouter", "deepseek/deepseek-r1", coding_quality=0.85, reasoning_quality=0.9, governance_reliability=0.7, hallucination_risk=0.25, latency_score=0.5, cost_score=0.2, context_window=65536, structured_output_reliability=0.7, replay_stability=0.7, semantic_consistency=0.75, sovereignty_level=SovereigntyLevel.SOVEREIGN_PREFERRED, operator_trust=0.7),
            ModelCapability("openrouter", "meta-llama/llama-3.1-70b-instruct", coding_quality=0.8, reasoning_quality=0.8, governance_reliability=0.65, hallucination_risk=0.3, latency_score=0.5, cost_score=0.3, context_window=131072, structured_output_reliability=0.6, replay_stability=0.65, semantic_consistency=0.7, sovereignty_level=SovereigntyLevel.SOVEREIGN_PREFERRED, operator_trust=0.65),
        ]
        for cap in defaults:
            self._capabilities[f"{cap.provider}/{cap.model}"] = cap

    def get_capability(self, provider: str, model: str) -> Optional[ModelCapability]:
        return self._capabilities.get(f"{provider}/{model}")

    def update_capability(self, capability: ModelCapability):
        self._capabilities[f"{capability.provider}/{capability.model}"] = capability

    def list_capabilities(self) -> List[ModelCapability]:
        return list(self._capabilities.values())

    def get_models_for_task(self, task_type: TaskType, sovereignty: SovereigntyLevel = SovereigntyLevel.HYBRID) -> List[ModelCapability]:
        candidates = []
        for cap in self._capabilities.values():
            if sovereignty == SovereigntyLevel.LOCAL_ONLY and cap.sovereignty_level != SovereigntyLevel.LOCAL_ONLY:
                continue
            if sovereignty == SovereigntyLevel.SOVEREIGN_REQUIRED and cap.sovereignty_level not in (SovereigntyLevel.LOCAL_ONLY, SovereigntyLevel.SOVEREIGN_PREFERRED):
                continue
            if sovereignty == SovereigntyLevel.FRONTIER_ONLY and cap.sovereignty_level == SovereigntyLevel.LOCAL_ONLY:
                continue
            score = self._score_for_task(cap, task_type)
            if score > 0.3:
                candidates.append((cap, score))
        candidates.sort(key=lambda x: x[1], reverse=True)
        return [c[0] for c in candidates]

    def _score_for_task(self, cap: ModelCapability, task_type: TaskType) -> float:
        weights = {
            TaskType.CODE_GENERATION: {"coding_quality": 0.4, "reasoning_quality": 0.3, "structured_output_reliability": 0.2, "replay_stability": 0.1},
            TaskType.ARCHITECTURE_REASONING: {"reasoning_quality": 0.5, "coding_quality": 0.2, "semantic_consistency": 0.2, "governance_reliability": 0.1},
            TaskType.GOVERNANCE_ANALYSIS: {"governance_reliability": 0.5, "reasoning_quality": 0.3, "replay_stability": 0.2},
            TaskType.REPLAY_ANALYSIS: {"replay_stability": 0.4, "reasoning_quality": 0.3, "semantic_consistency": 0.3},
            TaskType.SEMANTIC_EVALUATION: {"semantic_consistency": 0.4, "reasoning_quality": 0.3, "replay_stability": 0.3},
            TaskType.SPECIFICATION_GENERATION: {"structured_output_reliability": 0.4, "coding_quality": 0.3, "semantic_consistency": 0.3},
            TaskType.MUTATION_REASONING: {"reasoning_quality": 0.4, "coding_quality": 0.3, "replay_stability": 0.3},
            TaskType.DRIFT_ANALYSIS: {"semantic_consistency": 0.4, "reasoning_quality": 0.3, "governance_reliability": 0.3},
            TaskType.OPERATOR_EXPLANATION: {"reasoning_quality": 0.4, "semantic_consistency": 0.3, "operator_trust": 0.3},
            TaskType.MEMORY_CLASSIFICATION: {"semantic_consistency": 0.4, "reasoning_quality": 0.3, "structured_output_reliability": 0.3},
        }
        w = weights.get(task_type, {"reasoning_quality": 0.5, "coding_quality": 0.5})
        score = sum(getattr(cap, attr, 0.5) * weight for attr, weight in w.items())
        score *= (1.0 - cap.hallucination_risk * 0.5)
        score *= (1.0 - cap.historical_failure_rate)
        return max(0.0, min(1.0, score))


# ── Routing ─────────────────────────────────────────────────────────────────

@dataclass
class RoutingRequest:
    task_type: TaskType
    required_capabilities: List[str] = field(default_factory=list)
    governance_level: str = "standard"
    sovereignty_requirement: SovereigntyLevel = SovereigntyLevel.HYBRID
    latency_budget_ms: int = 30000
    cost_budget_usd: float = 1.0
    hallucination_tolerance: float = 0.3
    replay_sensitivity: str = "standard"
    context_size: int = 4096
    workspace_id: Optional[str] = None
    project_id: Optional[str] = None


@dataclass
class RoutingDecision:
    selected_model: str
    selected_provider: str
    routing_reason: str
    rejected_models: List[dict] = field(default_factory=list)
    trust_score: float = 0.5
    governance_score: float = 0.5
    sovereignty_score: float = 0.5
    cost_estimate: float = 0.0
    fallback_chain: List[dict] = field(default_factory=list)
    arbitration_required: bool = False


class CognitiveModelRouter:
    def __init__(self, registry: ModelCapabilityRegistry):
        self.registry = registry

    def route(self, request: RoutingRequest) -> RoutingDecision:
        candidates = self.registry.get_models_for_task(request.task_type, request.sovereignty_requirement)
        if not candidates:
            return RoutingDecision(selected_model="none", selected_provider="none",
                routing_reason="No suitable models found", rejected_models=[], trust_score=0.0,
                governance_score=0.0, sovereignty_score=0.0)

        scored = [(cap, self._score_candidate(cap, request)) for cap in candidates]
        scored.sort(key=lambda x: x[1], reverse=True)

        best = scored[0]
        rejected = [{"provider": c.provider, "model": c.model, "score": round(s, 3),
                      "reason": f"Lower score ({s:.3f}) than selected ({best[1]:.3f})"}
                    for c, s in scored[1:]]

        fallback = [{"provider": c.provider, "model": c.model, "score": round(s, 3)}
                    for c, s in scored[1:4]]

        arbitration = len(scored) >= 2 and abs(scored[0][1] - scored[1][1]) < 0.1

        reason = f"Selected {best[0].provider}/{best[0].model}. task={request.task_type.value}. sovereignty={request.sovereignty_requirement.value}. score={best[1]:.3f}"
        if arbitration:
            reason += ". ARBITRATION RECOMMENDED (close scores)"

        return RoutingDecision(
            selected_model=best[0].model, selected_provider=best[0].provider,
            routing_reason=reason, rejected_models=rejected,
            trust_score=best[0].operator_trust, governance_score=best[0].governance_reliability,
            sovereignty_score=1.0 if best[0].sovereignty_level in (SovereigntyLevel.LOCAL_ONLY, SovereigntyLevel.SOVEREIGN_PREFERRED) else 0.3,
            cost_estimate=self._estimate_cost(best[0], request.context_size),
            fallback_chain=fallback, arbitration_required=arbitration,
        )

    def _score_candidate(self, cap: ModelCapability, request: RoutingRequest) -> float:
        base = self.registry._score_for_task(cap, request.task_type)
        if request.governance_level == "strict":
            base *= (0.5 + cap.governance_reliability)
        if cap.hallucination_risk > request.hallucination_tolerance:
            base *= (1.0 - (cap.hallucination_risk - request.hallucination_tolerance))
        if request.replay_sensitivity == "high":
            base *= (0.5 + cap.replay_stability)
        return max(0.0, min(1.0, base))

    def _estimate_cost(self, cap: ModelCapability, context_size: int) -> float:
        if cap.cost_score == 0.0:
            return 0.0
        output_tokens = context_size // 4
        pricing = {"openai": (0.0025, 0.01), "anthropic": (0.003, 0.015), "openrouter": (0.001, 0.005)}
        pc, cc = pricing.get(cap.provider, (0.001, 0.005))
        return (context_size / 1000 * pc) + (output_tokens / 1000 * cc)


# ── Arbitration ─────────────────────────────────────────────────────────────

@dataclass
class ArbitrationResult:
    participating_models: List[dict] = field(default_factory=list)
    outputs: List[dict] = field(default_factory=list)
    consensus_score: float = 0.0
    contradiction_score: float = 0.0
    divergence_categories: List[str] = field(default_factory=list)
    arbitration_decision: str = ""
    confidence: float = 0.0
    governance_risk: float = 0.0
    replay_risk: float = 0.0
    escalation_required: bool = False
    human_review_required: bool = False


class CognitiveArbitrationEngine:
    def __init__(self, consensus_threshold: float = 0.7, contradiction_threshold: float = 0.5):
        self.consensus_threshold = consensus_threshold
        self.contradiction_threshold = contradiction_threshold

    async def arbitrate(self, outputs: List[dict], task_type: TaskType) -> ArbitrationResult:
        result = ArbitrationResult(
            participating_models=[{"provider": o.get("provider", ""), "model": o.get("model", "")} for o in outputs],
            outputs=outputs,
        )
        if len(outputs) < 2:
            result.consensus_score = 1.0
            result.arbitration_decision = "single_model"
            result.confidence = 0.5
            return result

        outputs_text = [o.get("output", "").strip() for o in outputs if o.get("success", True)]
        if not outputs_text:
            result.consensus_score = 0.0
            result.contradiction_score = 1.0
            result.arbitration_decision = "all_failed"
            result.escalation_required = True
            return result

        similarities = []
        for i in range(len(outputs_text)):
            for j in range(i + 1, len(outputs_text)):
                similarities.append(self._text_similarity(outputs_text[i], outputs_text[j]))

        avg_sim = sum(similarities) / len(similarities) if similarities else 0.0
        result.consensus_score = avg_sim
        result.contradiction_score = 1.0 - avg_sim

        if result.contradiction_score > self.contradiction_threshold:
            result.divergence_categories.append("semantic_divergence")
            if task_type in (TaskType.GOVERNANCE_ANALYSIS, TaskType.REPLAY_ANALYSIS):
                result.divergence_categories.append("governance_divergence")
                result.governance_risk = result.contradiction_score
            if task_type in (TaskType.REPLAY_ANALYSIS, TaskType.SEMANTIC_EVALUATION):
                result.divergence_categories.append("replay_risk")
                result.replay_risk = result.contradiction_score

        if result.consensus_score >= self.consensus_threshold:
            result.arbitration_decision = "consensus"
            result.confidence = result.consensus_score
        elif result.contradiction_score > self.contradiction_threshold:
            result.arbitration_decision = "disagreement_detected"
            result.confidence = 1.0 - result.contradiction_score
            result.escalation_required = True
            if result.governance_risk > 0.5 or result.replay_risk > 0.5:
                result.human_review_required = True
        else:
            result.arbitration_decision = "partial_consensus"
            result.confidence = result.consensus_score

        return result

    def _text_similarity(self, text1: str, text2: str) -> float:
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        if not words1 or not words2:
            return 0.0
        intersection = words1 & words2
        union = words1 | words2
        return len(intersection) / len(union) if union else 0.0


# ── Global Instances ───────────────────────────────────────────────────────

_registry = ModelCapabilityRegistry()
_router = CognitiveModelRouter(_registry)
_arbitration = CognitiveArbitrationEngine()


def get_capability_registry() -> ModelCapabilityRegistry:
    return _registry

def get_model_router() -> CognitiveModelRouter:
    return _router

def get_arbitration_engine() -> CognitiveArbitrationEngine:
    return _arbitration
