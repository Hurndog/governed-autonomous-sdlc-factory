"""Cost ledger for tracking all model and tool usage costs."""
import csv
import json
import os
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
from src.core.logging import get_logger

logger = get_logger("cost-ledger")


# Default cost per 1K tokens (USD)
MODEL_COSTS = {
    "local-model": {"in": 0.0, "out": 0.0},
    "gpt-4": {"in": 0.03, "out": 0.06},
    "gpt-4-turbo": {"in": 0.01, "out": 0.03},
    "gpt-3.5-turbo": {"in": 0.0005, "out": 0.0015},
    "claude-3-opus": {"in": 0.015, "out": 0.075},
    "claude-3-sonnet": {"in": 0.003, "out": 0.015},
    "claude-3-haiku": {"in": 0.00025, "out": 0.00125},
}


class CostLedger:
    """Tracks and reports all costs for SDLC runs."""

    def __init__(self, logs_dir: str = None):
        self.logs_dir = logs_dir or os.path.join(os.path.dirname(__file__), "..", "..", "logs")
        os.makedirs(self.logs_dir, exist_ok=True)
        self.events: List[Dict[str, Any]] = []

    def estimate_cost(self, model_name: str, tokens_in: int, tokens_out: int) -> float:
        """Estimate cost for a model call."""
        costs = MODEL_COSTS.get(model_name, {"in": 0.0, "out": 0.0})
        return (tokens_in / 1000) * costs["in"] + (tokens_out / 1000) * costs["out"]

    def record_model_call(self, run_id: str, model_name: str, provider: str,
                          tokens_in: int, tokens_out: int, is_local: bool = True,
                          latency_ms: float = None, phase_id: str = None,
                          agent_id: str = None) -> Dict[str, Any]:
        estimated = self.estimate_cost(model_name, tokens_in, tokens_out)
        event = {
            "id": f"cost-{len(self.events)}",
            "run_id": run_id,
            "phase_id": phase_id,
            "agent_id": agent_id,
            "event_type": "model_call",
            "model_name": model_name,
            "provider": provider,
            "tokens_in": tokens_in,
            "tokens_out": tokens_out,
            "estimated_cost": round(estimated, 6),
            "actual_cost": None,
            "is_local": is_local,
            "latency_ms": latency_ms,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        self.events.append(event)
        return event

    def record_tool_call(self, run_id: str, tool_name: str, server_name: str,
                         is_success: bool, latency_ms: float = None,
                         phase_id: str = None, agent_id: str = None) -> Dict[str, Any]:
        event = {
            "id": f"cost-{len(self.events)}",
            "run_id": run_id,
            "phase_id": phase_id,
            "agent_id": agent_id,
            "event_type": "tool_call",
            "tool_name": tool_name,
            "server_name": server_name,
            "is_success": is_success,
            "latency_ms": latency_ms,
            "estimated_cost": 0.0,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        self.events.append(event)
        return event

    def get_run_report(self, run_id: str) -> Dict[str, Any]:
        run_events = [e for e in self.events if e["run_id"] == run_id]
        total = sum(e.get("estimated_cost", 0) for e in run_events)
        local = sum(e.get("estimated_cost", 0) for e in run_events if e.get("is_local"))
        paid = sum(e.get("estimated_cost", 0) for e in run_events if not e.get("is_local"))

        by_phase = {}
        by_agent = {}
        by_model = {}
        for e in run_events:
            pk = e.get("phase_id", "unknown")
            by_phase[pk] = by_phase.get(pk, 0) + e.get("estimated_cost", 0)
            ak = e.get("agent_id", "unknown")
            by_agent[ak] = by_agent.get(ak, 0) + e.get("estimated_cost", 0)
            mk = e.get("model_name", "unknown")
            by_model[mk] = by_model.get(mk, 0) + e.get("estimated_cost", 0)

        return {
            "run_id": run_id,
            "total_cost": round(total, 4),
            "local_cost": round(local, 4),
            "paid_cost": round(paid, 4),
            "estimated_savings": round(paid * 0.9, 4) if paid > 0 else 0.0,
            "event_count": len(run_events),
            "by_phase": {k: round(v, 4) for k, v in by_phase.items()},
            "by_agent": {k: round(v, 4) for k, v in by_agent.items()},
            "by_model": {k: round(v, 4) for k, v in by_model.items()},
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }

    def export_csv(self, run_id: str) -> str:
        path = os.path.join(self.logs_dir, f"{run_id}-cost-ledger.csv")
        run_events = [e for e in self.events if e["run_id"] == run_id]
        with open(path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["timestamp", "run_id", "phase_id", "agent_id",
                                                     "event_type", "model_name", "provider",
                                                     "tokens_in", "tokens_out", "estimated_cost",
                                                     "is_local", "latency_ms"])
            writer.writeheader()
            for e in run_events:
                writer.writerow({k: e.get(k, "") for k in ["timestamp", "run_id", "phase_id", "agent_id",
                                                            "event_type", "model_name", "provider",
                                                            "tokens_in", "tokens_out", "estimated_cost",
                                                            "is_local", "latency_ms"]})
        return path

    def export_json(self, run_id: str) -> str:
        path = os.path.join(self.logs_dir, f"{run_id}-cost-ledger.json")
        report = self.get_run_report(run_id)
        with open(path, "w") as f:
            json.dump(report, f, indent=2)
        return path

    def generate_report_md(self, run_id: str, budget_limit: float = None) -> str:
        report = self.get_run_report(run_id)
        lines = [
            f"# Cost Report — Run {run_id}",
            f"",
            f"**Generated:** {report['generated_at']}",
            f"",
            f"## Summary",
            f"",
            f"| Metric | Value |",
            f"|--------|-------|",
            f"| Total Cost | ${report['total_cost']:.4f} |",
            f"| Local Model Cost | ${report['local_cost']:.4f} |",
            f"| Paid Model Cost | ${report['paid_cost']:.4f} |",
            f"| Estimated Savings | ${report['estimated_savings']:.4f} |",
            f"| Event Count | {report['event_count']} |",
        ]
        if budget_limit:
            lines.append(f"| Budget Limit | ${budget_limit:.2f} |")
            lines.append(f"| Remaining | ${budget_limit - report['total_cost']:.2f} |")
        lines.extend([f"", f"## By Phase", f""])
        for phase, cost in report.get("by_phase", {}).items():
            lines.append(f"- **{phase}**: ${cost:.4f}")
        lines.extend([f"", f"## By Model", f""])
        for model, cost in report.get("by_model", {}).items():
            lines.append(f"- **{model}**: ${cost:.4f}")
        return "\n".join(lines)
