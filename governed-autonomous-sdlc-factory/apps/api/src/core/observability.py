"""Observability: OpenTelemetry, Prometheus metrics, and health tracking."""
import time
from typing import Optional
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from fastapi import Response

# Run metrics
RUNS_CREATED = Counter("sdlc_runs_created_total", "Total runs created")
RUNS_COMPLETED = Counter("sdlc_runs_completed_total", "Total runs completed", ["status"])
RUN_DURATION = Histogram("sdlc_run_duration_seconds", "Run duration in seconds")
PHASE_DURATION = Histogram("sdlc_phase_duration_seconds", "Phase duration in seconds", ["phase_name"])
TASK_DURATION = Histogram("sdlc_task_duration_seconds", "Task duration in seconds", ["task_type"])

# Model metrics
MODEL_CALLS = Counter("sdlc_model_calls_total", "Total model calls", ["model", "provider", "status"])
MODEL_LATENCY = Histogram("sdlc_model_latency_seconds", "Model call latency", ["model"])
MODEL_TOKENS = Counter("sdlc_model_tokens_total", "Total tokens", ["model", "direction"])
MODEL_COST = Counter("sdlc_model_cost_usd_total", "Total model cost in USD", ["model", "provider"])

# Tool metrics
TOOL_CALLS = Counter("sdlc_tool_calls_total", "Total tool calls", ["tool", "server", "status"])
TOOL_LATENCY = Histogram("sdlc_tool_latency_seconds", "Tool call latency", ["tool"])

# Cost metrics
COST_TOTAL = Counter("sdlc_cost_usd_total", "Total cost in USD", ["run_id", "phase"])
BUDGET_REMAINING = Gauge("sdlc_budget_remaining_usd", "Remaining budget", ["run_id"])

# Queue and system metrics
QUEUE_DEPTH = Gauge("sdlc_queue_depth", "Current queue depth")
ACTIVE_RUNS = Gauge("sdlc_active_runs", "Currently active runs")
FAILURE_COUNT = Counter("sdlc_failures_total", "Total failures", ["type", "phase"])
RETRY_COUNT = Counter("sdlc_retries_total", "Total retries", ["agent", "phase"])

# Deployment metrics
DEPLOYMENT_STATUS = Gauge("sdlc_deployment_status", "Deployment status (0=down, 1=up)", ["project"])
DEPLOYMENT_HEALTH = Gauge("sdlc_deployment_health", "Deployment health check (0=fail, 1=pass)", ["project"])

# ── Phase 10-16: Replay & Integrity Metrics ──────────────────────────────

REPLAY_SESSIONS = Counter("sdlc_replay_sessions_total", "Total replay sessions", ["mode", "status"])
REPLAY_DURATION = Histogram("sdlc_replay_duration_seconds", "Replay duration", ["mode"])
REPLAY_EVENTS = Counter("sdlc_replay_events_total", "Total events replayed", ["mode"])
REPLAY_DIVERGENCES = Counter("sdlc_replay_divergences_total", "Total divergences detected", ["severity"])

INTEGRITY_CHECKS = Counter("sdlc_integrity_checks_total", "Total integrity checks", ["type", "status"])
INTEGRITY_SCORE = Gauge("sdlc_integrity_score", "Integrity score per run", ["run_id"])
INTEGRITY_VERIFICATION_DURATION = Histogram("sdlc_integrity_verification_seconds", "Integrity verification duration")

DIVERGENCE_DETECTED = Counter("sdlc_divergence_detected_total", "Divergences detected", ["type", "severity"])

CHAIN_VERIFICATIONS = Counter("sdlc_chain_verifications_total", "Chain verifications", ["status"])
SNAPSHOT_LOAD_DURATION = Histogram("sdlc_snapshot_load_seconds", "Snapshot load duration")
SEMANTIC_GRAPH_TRAVERSAL = Histogram("sdlc_semantic_graph_traversal_seconds", "Semantic graph traversal duration")


def get_prometheus_metrics() -> Response:
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST,
    )


class Timer:
    """Context manager for timing operations."""
    def __init__(self, histogram: Histogram, labels: Optional[dict] = None):
        self.histogram = histogram
        self.labels = labels or {}
        self.start = None

    def __enter__(self):
        self.start = time.time()
        return self

    def __exit__(self, *args):
        duration = time.time() - self.start
        if self.labels:
            self.histogram.labels(**self.labels).observe(duration)
        else:
            self.histogram.observe(duration)
