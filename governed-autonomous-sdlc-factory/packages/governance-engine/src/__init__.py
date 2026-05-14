"""Governance engine with OPA Rego policy evaluation."""
import json
import os
import subprocess
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone
from src.core.logging import get_logger

logger = get_logger("governance")


class GovernanceEngine:
    """Evaluates governance policies against run state."""

    def __init__(self, policies_dir: str = None):
        self.policies_dir = policies_dir or os.path.join(
            os.path.dirname(__file__), "..", "..", "policies", "opa"
        )
        self.opa_available = self._check_opa()

    def _check_opa(self) -> bool:
        try:
            result = subprocess.run(
                ["opa", "version"], capture_output=True, text=True, timeout=5
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            logger.warning("OPA not available, using built-in policy evaluation")
            return False

    def evaluate_policy(self, policy_name: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate a single policy."""
        if self.opa_available:
            return self._evaluate_opa(policy_name, input_data)
        return self._evaluate_builtin(policy_name, input_data)

    def _evaluate_opa(self, policy_name: str, input_data: Dict) -> Dict:
        policy_path = os.path.join(self.policies_dir, f"{policy_name}.rego")
        if not os.path.exists(policy_path):
            return {"decision": "error", "details": f"Policy file not found: {policy_path}"}
        try:
            result = subprocess.run(
                ["opa", "eval", "--data", policy_path, "--input", "-", "--format", "json",
                 "data.sdlc_factory.allow"],
                input=json.dumps({"input": input_data}),
                capture_output=True, text=True, timeout=30,
            )
            if result.returncode == 0:
                output = json.loads(result.stdout)
                return {"decision": "allow" if output.get("result", [{}])[0].get("expressions", [{}])[0].get("value", False) else "deny"}
            return {"decision": "error", "details": result.stderr}
        except Exception as e:
            return {"decision": "error", "details": str(e)}

    def _evaluate_builtin(self, policy_name: str, input_data: Dict) -> Dict:
        """Built-in policy evaluation when OPA is not available."""
        policies = {
            "no_build_without_approved_spec": self._policy_no_build_without_spec,
            "no_direct_push_to_main": self._policy_no_push_main,
            "no_deploy_without_tests": self._policy_no_deploy_without_tests,
            "no_deploy_without_security": self._policy_no_deploy_without_security,
            "no_deploy_without_governance": self._policy_no_deploy_without_governance,
            "no_paid_model_without_policy": self._policy_no_paid_model,
            "no_tool_without_mcp_permission": self._policy_no_tool_without_mcp,
            "no_secret_in_repo": self._policy_no_secret,
            "no_migration_without_rollback": self._policy_no_migration_no_rollback,
            "no_high_risk_dependency": self._policy_no_high_risk_dep,
            "no_missing_readme": self._policy_no_missing_readme,
            "no_missing_env_example": self._policy_no_missing_env,
            "no_missing_test_plan": self._policy_no_missing_test_plan,
            "no_missing_architecture": self._policy_no_missing_arch,
            "no_missing_evidence": self._policy_no_missing_evidence,
        }
        policy_fn = policies.get(policy_name)
        if policy_fn:
            return policy_fn(input_data)
        return {"decision": "allow", "details": f"Unknown policy: {policy_name}, defaulting to allow"}

    def _policy_no_build_without_spec(self, data: Dict) -> Dict:
        has_approved_spec = data.get("has_approved_specification", False)
        return {"decision": "allow" if has_approved_spec else "deny",
                "details": "Specification baseline must be approved before build"}

    def _policy_no_push_main(self, data: Dict) -> Dict:
        branch = data.get("branch", "")
        return {"decision": "deny" if branch == "main" else "allow",
                "details": "Direct push to main is not allowed"}

    def _policy_no_deploy_without_tests(self, data: Dict) -> Dict:
        tests_passed = data.get("tests_passed", False)
        return {"decision": "allow" if tests_passed else "deny",
                "details": "Tests must pass before deployment"}

    def _policy_no_deploy_without_security(self, data: Dict) -> Dict:
        critical_findings = data.get("critical_security_findings", 0)
        return {"decision": "deny" if critical_findings > 0 else "allow",
                "details": f"{critical_findings} critical security findings must be resolved"}

    def _policy_no_deploy_without_governance(self, data: Dict) -> Dict:
        governance_passed = data.get("governance_checks_passed", False)
        return {"decision": "allow" if governance_passed else "deny",
                "details": "Governance checks must pass before deployment"}

    def _policy_no_paid_model(self, data: Dict) -> Dict:
        is_local = data.get("is_local", True)
        local_only = data.get("local_only_mode", True)
        return {"decision": "deny" if (not is_local and local_only) else "allow",
                "details": "Paid model usage not allowed in local-only mode"}

    def _policy_no_tool_without_mcp(self, data: Dict) -> Dict:
        has_permission = data.get("has_mcp_permission", False)
        return {"decision": "allow" if has_permission else "deny",
                "details": "Tool call requires MCP permission"}

    def _policy_no_secret(self, data: Dict) -> Dict:
        has_secrets = data.get("has_secrets_in_code", False)
        return {"decision": "deny" if has_secrets else "allow",
                "details": "Secrets must not be committed to repository"}

    def _policy_no_migration_no_rollback(self, data: Dict) -> Dict:
        has_rollback = data.get("has_rollback_note", False)
        is_migration = data.get("is_migration", False)
        if not is_migration:
            return {"decision": "allow", "details": "Not a migration"}
        return {"decision": "allow" if has_rollback else "deny",
                "details": "Database migrations must include rollback notes"}

    def _policy_no_high_risk_dep(self, data: Dict) -> Dict:
        is_high_risk = data.get("is_high_risk_dependency", False)
        is_approved = data.get("is_dependency_approved", False)
        if not is_high_risk:
            return {"decision": "allow", "details": "Not a high-risk dependency"}
        return {"decision": "allow" if is_approved else "deny",
                "details": "High-risk dependencies require approval"}

    def _policy_no_missing_readme(self, data: Dict) -> Dict:
        has_readme = data.get("has_readme", False)
        return {"decision": "allow" if has_readme else "deny",
                "details": "README.md is required"}

    def _policy_no_missing_env(self, data: Dict) -> Dict:
        has_env = data.get("has_env_example", False)
        return {"decision": "allow" if has_env else "deny",
                "details": ".env.example is required"}

    def _policy_no_missing_test_plan(self, data: Dict) -> Dict:
        has_plan = data.get("has_test_plan", False)
        return {"decision": "allow" if has_plan else "deny",
                "details": "Test plan is required"}

    def _policy_no_missing_arch(self, data: Dict) -> Dict:
        has_arch = data.get("has_architecture_doc", False)
        return {"decision": "allow" if has_arch else "deny",
                "details": "Architecture document is required"}

    def _policy_no_missing_evidence(self, data: Dict) -> Dict:
        has_evidence = data.get("has_evidence_bundle", False)
        return {"decision": "allow" if has_evidence else "deny",
                "details": "Evidence bundle is required"}

    def evaluate_all(self, run_state: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Evaluate all governance policies for a run."""
        results = []
        policy_inputs = {
            "no_build_without_approved_spec": {"has_approved_specification": run_state.get("spec_baseline_locked", False)},
            "no_direct_push_to_main": {"branch": run_state.get("branch", "")},
            "no_deploy_without_tests": {"tests_passed": run_state.get("tests_passed", False)},
            "no_deploy_without_security": {"critical_security_findings": run_state.get("critical_findings", 0)},
            "no_deploy_without_governance": {"governance_checks_passed": run_state.get("governance_passed", False)},
            "no_missing_readme": {"has_readme": run_state.get("has_readme", False)},
            "no_missing_env_example": {"has_env_example": run_state.get("has_env_example", False)},
            "no_missing_test_plan": {"has_test_plan": run_state.get("has_test_plan", False)},
            "no_missing_architecture": {"has_architecture_doc": run_state.get("has_architecture_doc", False)},
            "no_missing_evidence": {"has_evidence_bundle": run_state.get("has_evidence_bundle", False)},
        }
        for policy_name, input_data in policy_inputs.items():
            result = self.evaluate_policy(policy_name, input_data)
            results.append({
                "policy_name": policy_name,
                "decision": result["decision"],
                "input": input_data,
                "output": result,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            })
        return results

    def generate_report(self, results: List[Dict]) -> Dict[str, Any]:
        passed = [r for r in results if r["decision"] == "allow"]
        failed = [r for r in results if r["decision"] == "deny"]
        errors = [r for r in results if r["decision"] == "error"]
        return {
            "total": len(results),
            "passed": len(passed),
            "failed": len(failed),
            "errors": len(errors),
            "can_proceed": len(failed) == 0 and len(errors) == 0,
            "findings": results,
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }
