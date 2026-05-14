"""Evidence engine for creating evidence bundles."""
import json
import os
import zipfile
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
from src.core.logging import get_logger

logger = get_logger("evidence")


class EvidenceEngine:
    """Creates and manages evidence bundles for SDLC runs."""

    def __init__(self, evidence_dir: str = None):
        self.evidence_dir = evidence_dir or os.path.join(os.path.dirname(__file__), "..", "..", "evidence")
        os.makedirs(self.evidence_dir, exist_ok=True)

    def create_bundle_dir(self, run_id: str) -> str:
        bundle_dir = os.path.join(self.evidence_dir, "runs", run_id)
        os.makedirs(bundle_dir, exist_ok=True)
        return bundle_dir

    def write_requirements_trace(self, run_id: str, requirements: List[Dict]) -> str:
        path = os.path.join(self.create_bundle_dir(run_id), "requirements_trace.json")
        with open(path, "w") as f:
            json.dump({"requirements": requirements, "generated_at": datetime.now(timezone.utc).isoformat()}, f, indent=2)
        return path

    def write_design_trace(self, run_id: str, designs: List[Dict]) -> str:
        path = os.path.join(self.create_bundle_dir(run_id), "design_trace.json")
        with open(path, "w") as f:
            json.dump({"designs": designs, "generated_at": datetime.now(timezone.utc).isoformat()}, f, indent=2)
        return path

    def write_architecture_trace(self, run_id: str, architecture: Dict) -> str:
        path = os.path.join(self.create_bundle_dir(run_id), "architecture_trace.json")
        with open(path, "w") as f:
            json.dump(architecture, f, indent=2)
        return path

    def write_code_trace(self, run_id: str, files: List[Dict]) -> str:
        path = os.path.join(self.create_bundle_dir(run_id), "code_trace.json")
        with open(path, "w") as f:
            json.dump({"files": files, "generated_at": datetime.now(timezone.utc).isoformat()}, f, indent=2)
        return path

    def write_test_results(self, run_id: str, results: List[Dict]) -> str:
        path = os.path.join(self.create_bundle_dir(run_id), "test_results.json")
        with open(path, "w") as f:
            json.dump({"results": results, "generated_at": datetime.now(timezone.utc).isoformat()}, f, indent=2)
        return path

    def write_security_results(self, run_id: str, findings: List[Dict]) -> str:
        path = os.path.join(self.create_bundle_dir(run_id), "security_results.json")
        with open(path, "w") as f:
            json.dump({"findings": findings, "generated_at": datetime.now(timezone.utc).isoformat()}, f, indent=2)
        return path

    def write_governance_results(self, run_id: str, findings: List[Dict]) -> str:
        path = os.path.join(self.create_bundle_dir(run_id), "governance_results.json")
        with open(path, "w") as f:
            json.dump({"findings": findings, "generated_at": datetime.now(timezone.utc).isoformat()}, f, indent=2)
        return path

    def write_cost_report(self, run_id: str, report: Dict) -> str:
        path = os.path.join(self.create_bundle_dir(run_id), "cost_report.json")
        with open(path, "w") as f:
            json.dump(report, f, indent=2)
        return path

    def write_deployment_report(self, run_id: str, report: Dict) -> str:
        path = os.path.join(self.create_bundle_dir(run_id), "deployment_report.json")
        with open(path, "w") as f:
            json.dump(report, f, indent=2)
        return path

    def write_refactor_history(self, run_id: str, history: List[Dict]) -> str:
        path = os.path.join(self.create_bundle_dir(run_id), "refactor_history.json")
        with open(path, "w") as f:
            json.dump({"history": history}, f, indent=2)
        return path

    def write_model_calls(self, run_id: str, calls: List[Dict]) -> str:
        path = os.path.join(self.create_bundle_dir(run_id), "model_calls.jsonl")
        with open(path, "w") as f:
            for call in calls:
                f.write(json.dumps(call) + "\n")
        return path

    def write_tool_calls(self, run_id: str, calls: List[Dict]) -> str:
        path = os.path.join(self.create_bundle_dir(run_id), "tool_calls.jsonl")
        with open(path, "w") as f:
            for call in calls:
                f.write(json.dumps(call) + "\n")
        return path

    def write_run_log(self, run_id: str, events: List[Dict]) -> str:
        path = os.path.join(self.create_bundle_dir(run_id), "run_log.jsonl")
        with open(path, "w") as f:
            for event in events:
                f.write(json.dumps(event) + "\n")
        return path

    def write_agent_traces(self, run_id: str, traces: List[Dict]) -> str:
        path = os.path.join(self.create_bundle_dir(run_id), "agent_traces.jsonl")
        with open(path, "w") as f:
            for trace in traces:
                f.write(json.dumps(trace) + "\n")
        return path

    def write_github_events(self, run_id: str, events: List[Dict]) -> str:
        path = os.path.join(self.create_bundle_dir(run_id), "github_events.jsonl")
        with open(path, "w") as f:
            for event in events:
                f.write(json.dumps(event) + "\n")
        return path

    def build_traceability_matrix(self, run_id: str, requirements: List[Dict],
                                   designs: List[Dict], architecture: Dict,
                                   code_files: List[Dict], test_cases: List[Dict],
                                   governance_checks: List[Dict],
                                   commits: List[Dict], deployment: Dict) -> str:
        path = os.path.join(self.create_bundle_dir(run_id), "traceability_matrix.json")
        matrix = {
            "requirements_to_designs": [],
            "requirements_to_architecture": [],
            "requirements_to_code": [],
            "requirements_to_tests": [],
            "requirements_to_governance": [],
            "requirements_to_commits": [],
            "requirements_to_deployment": [],
        }
        for req in requirements:
            req_id = req.get("id", req.get("req_id", "unknown"))
            matrix["requirements_to_designs"].append({"requirement": req_id, "designs": [d.get("id", "all") for d in designs]})
            matrix["requirements_to_architecture"].append({"requirement": req_id, "components": list(architecture.get("components", {}).keys())})
            matrix["requirements_to_code"].append({"requirement": req_id, "files": [f.get("path", "all") for f in code_files]})
            matrix["requirements_to_tests"].append({"requirement": req_id, "test_cases": [t.get("id", "all") for t in test_cases]})
            matrix["requirements_to_governance"].append({"requirement": req_id, "checks": [g.get("policy_name", "all") for g in governance_checks]})
            matrix["requirements_to_commits"].append({"requirement": req_id, "commits": [c.get("hash", "all") for c in commits]})
            matrix["requirements_to_deployment"].append({"requirement": req_id, "deployment": deployment.get("status", "unknown")})
        with open(path, "w") as f:
            json.dump(matrix, f, indent=2)
        return path

    def create_evidence_bundle_zip(self, run_id: str) -> str:
        """Create a zip file containing all evidence for a run."""
        bundle_dir = self.create_bundle_dir(run_id)
        zip_path = os.path.join(self.evidence_dir, "runs", f"{run_id}-evidence-bundle.zip")
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for root, dirs, files in os.walk(bundle_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, bundle_dir)
                    zf.write(file_path, arcname)
        logger.info(f"Evidence bundle created: {zip_path}")
        return zip_path

    def generate_summary(self, run_id: str) -> Dict[str, Any]:
        bundle_dir = self.create_bundle_dir(run_id)
        files = []
        total_size = 0
        for f in os.listdir(bundle_dir):
            fp = os.path.join(bundle_dir, f)
            if os.path.isfile(fp):
                size = os.path.getsize(fp)
                files.append({"name": f, "size_bytes": size})
                total_size += size
        return {
            "run_id": run_id,
            "bundle_dir": bundle_dir,
            "files": files,
            "total_size_bytes": total_size,
            "file_count": len(files),
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }
