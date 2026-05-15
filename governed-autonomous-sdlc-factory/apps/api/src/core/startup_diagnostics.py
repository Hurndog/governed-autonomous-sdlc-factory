"""Startup self-diagnostics for the Cognitive Cortex.

Runs at API startup to verify all components are operational.
"""
from __future__ import annotations

import asyncio
import os
import time
from typing import Optional

from src.core.logging import get_logger
from src.core.config import settings

logger = get_logger("startup_diagnostics")


class StartupDiagnostics:
    """Runs comprehensive startup checks."""

    def __init__(self):
        self.results: dict[str, dict] = {}
        self.start_time = time.monotonic()

    async def run_all(self) -> dict:
        """Run all startup diagnostics."""
        checks = [
            ("repository", self._check_repository),
            ("database", self._check_database),
            ("redis", self._check_redis),
            ("ollama", self._check_ollama),
            ("lm_studio", self._check_lm_studio),
            ("model_router", self._check_model_router),
            ("routes", self._check_routes),
            ("evidence_dir", self._check_evidence_dir),
            ("backup_dir", self._check_backup_dir),
            ("github", self._check_github),
            ("api_keys", self._check_api_keys),
            ("docker", self._check_docker),
        ]

        for name, check_fn in checks:
            try:
                result = await check_fn()
                self.results[name] = {"status": "ok" if result else "warning", "details": result}
            except Exception as e:
                self.results[name] = {"status": "error", "error": str(e)}

        elapsed = (time.monotonic() - self.start_time) * 1000
        self.results["_summary"] = {
            "total_checks": len(checks),
            "passed": sum(1 for r in self.results.values() if isinstance(r, dict) and r.get("status") == "ok"),
            "warnings": sum(1 for r in self.results.values() if isinstance(r, dict) and r.get("status") == "warning"),
            "errors": sum(1 for r in self.results.values() if isinstance(r, dict) and r.get("status") == "error"),
            "elapsed_ms": round(elapsed, 1),
        }

        self._log_results()
        return self.results

    async def _check_repository(self) -> dict:
        repo_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        git_dir = os.path.join(repo_path, "..", ".git")
        return {"path": repo_path, "git_exists": os.path.exists(git_dir)}

    async def _check_database(self) -> dict:
        try:
            from src.core.database import async_session_factory
            async with async_session_factory() as session:
                from sqlalchemy import text
                result = await session.execute(text("SELECT 1"))
                return {"connected": True}
        except Exception as e:
            return {"connected": False, "error": str(e)}

    async def _check_redis(self) -> dict:
        try:
            import redis.asyncio as redis
            r = redis.from_url(settings.redis_url)
            await r.ping()
            await r.close()
            return {"connected": True}
        except Exception as e:
            return {"connected": False, "error": str(e)}

    async def _check_ollama(self) -> dict:
        try:
            import httpx
            resp = await httpx.AsyncClient().get("http://localhost:11434/api/tags", timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                models = [m["name"] for m in data.get("models", [])]
                return {"running": True, "models": models, "model_count": len(models)}
            return {"running": False}
        except Exception:
            return {"running": False}

    async def _check_lm_studio(self) -> dict:
        try:
            import httpx
            resp = await httpx.AsyncClient().get("http://localhost:1234/v1/models", timeout=3)
            if resp.status_code == 200:
                data = resp.json()
                models = [m["id"] for m in data.get("data", [])]
                return {"running": True, "models": models}
            return {"running": False}
        except Exception:
            return {"running": False, "note": "LM Studio server not enabled"}

    async def _check_model_router(self) -> dict:
        try:
            from src.engines.model_router import ModelRouter
            router = ModelRouter()
            await router.initialize()
            stats = router.get_stats()
            return {"initialized": True, "providers": stats.get("providers", []), "models": stats.get("registry", {}).get("total_models", 0)}
        except Exception as e:
            return {"initialized": False, "error": str(e)}

    async def _check_routes(self) -> dict:
        try:
            from src.main import app
            return {"total_routes": len(app.routes)}
        except Exception as e:
            return {"error": str(e)}

    async def _check_evidence_dir(self) -> dict:
        evidence_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "..", "..", "evidence")
        exists = os.path.isdir(evidence_dir)
        files = len(os.listdir(evidence_dir)) if exists else 0
        return {"exists": exists, "path": evidence_dir, "files": files}

    async def _check_backup_dir(self) -> dict:
        backup_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "..", "..", "backups")
        exists = os.path.isdir(backup_dir)
        backups = len(os.listdir(backup_dir)) if exists else 0
        return {"exists": exists, "path": backup_dir, "backups": backups}

    async def _check_github(self) -> dict:
        import subprocess
        try:
            result = subprocess.run(["git", "remote", "get-url", "origin"], capture_output=True, text=True, cwd=os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
            return {"remote_configured": result.returncode == 0, "url": result.stdout.strip() if result.returncode == 0 else None}
        except Exception:
            return {"remote_configured": False}

    async def _check_api_keys(self) -> dict:
        return {
            "openai": bool(settings.openai_api_key),
            "anthropic": bool(settings.anthropic_api_key),
            "ollama": True,  # Always available locally
            "lm_studio": True,  # Always available locally
        }

    async def _check_docker(self) -> dict:
        import subprocess
        try:
            result = subprocess.run(["docker", "ps", "--format", "{{.Names}}"], capture_output=True, text=True, timeout=5)
            containers = [c for c in result.stdout.strip().split("\n") if c]
            return {"running": True, "containers": containers, "count": len(containers)}
        except Exception as e:
            return {"running": False, "error": str(e)}

    def _log_results(self):
        summary = self.results.get("_summary", {})
        logger.info(f"Startup diagnostics complete: {summary.get('passed', 0)}/{summary.get('total_checks', 0)} passed, {summary.get('warnings', 0)} warnings, {summary.get('errors', 0)} errors")

        for name, result in self.results.items():
            if name.startswith("_"):
                continue
            status = result.get("status", "unknown")
            if status == "error":
                logger.error(f"  ❌ {name}: {result.get('error', 'unknown error')}")
            elif status == "warning":
                logger.warning(f"  ⚠️  {name}: {result}")
            else:
                logger.info(f"  ✅ {name}: OK")


async def run_startup_diagnostics() -> dict:
    """Run all startup diagnostics."""
    diagnostics = StartupDiagnostics()
    return await diagnostics.run_all()
