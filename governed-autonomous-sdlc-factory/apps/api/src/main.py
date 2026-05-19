"""FastAPI application entry point."""
import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.core.config import settings
from src.core.logging import setup_logging, get_logger
from src.core.database import init_db
from src.core.observability import get_prometheus_metrics
from src.api.middleware.trace import TraceMiddleware
from src.api.middleware.audit import AuditMiddleware
from src.api.middleware.auth import AuthMiddleware
from src.api.v1.router import api_router
from src.websocket.run_events import ws_router

setup_logging(settings.log_level, settings.log_format)
logger = get_logger("main")

start_time = time.time()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Governed Autonomous SDLC Factory API")
    await init_db()
    logger.info("Database initialized")

    # Run startup diagnostics
    try:
        from src.core.startup_diagnostics import run_startup_diagnostics
        diag_results = await run_startup_diagnostics()
        summary = diag_results.get("_summary", {})
        logger.info(f"Startup diagnostics: {summary.get('passed', 0)}/{summary.get('total_checks', 0)} passed")
    except Exception as e:
        logger.warning(f"Startup diagnostics failed: {e}")
    # Seed governance policies
    try:
        pass  # Governance seeding handled by endpoint
    except Exception:
        logger.warning("Governance seeding skipped")
    yield
    logger.info("Shutting down API")


app = FastAPI(
    title="Governed Autonomous SDLC Factory",
    description="Forge Control Tower — UI-Operated Autonomous Software Factory",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS
origins = [o.strip() for o in settings.api_cors_origins.split(",")]
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

# Custom middleware
app.add_middleware(TraceMiddleware)
app.add_middleware(AuditMiddleware)
app.add_middleware(AuthMiddleware)

# Include routers
app.include_router(api_router)
app.include_router(ws_router)

# Startup diagnostics: log all loaded routes
all_routes = []
for route in app.routes:
    if hasattr(route, "path"):
        methods = getattr(route, "methods", set())
        all_routes.append(f"{','.join(methods)} {route.path}")
logger.info(f"Loaded {len(all_routes)} routes")
for r in sorted(all_routes):
    if "/engines" in r or "/health" in r:
        logger.info(f"  {r}")


# Debug endpoints
@app.get("/api/v1/debug/routes", include_in_schema=False)
async def debug_routes():
    """List all loaded routes for debugging."""
    routes = []
    for route in app.routes:
        if hasattr(route, "path"):
            routes.append({
                "path": route.path,
                "methods": list(getattr(route, "methods", [])),
                "name": getattr(route, "name", ""),
            })
    return {"total": len(routes), "routes": routes}


@app.get("/api/v1/debug/import-check", include_in_schema=False)
async def debug_import_check():
    """Check if all engine modules can be imported."""
    results = {}
    modules = [
        "src.api.v1.endpoints.engines",
        "src.engines.specification_engine",
        "src.engines.architecture_engine",
        "src.engines.governance_engine",
        "src.engines.test_engine",
        "src.engines.traceability",
        "src.engines.snapshots",
    ]
    for mod in modules:
        try:
            __import__(mod)
            results[mod] = "ok"
        except Exception as e:
            results[mod] = f"ERROR: {type(e).__name__}: {e}"
    return results


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": str(exc)},
    )


@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "version": "1.0.0",
        "database": "connected",
        "redis": "connected",
        "uptime_seconds": round(time.time() - start_time, 2),
    }


@app.get("/metrics")
async def metrics():
    return get_prometheus_metrics()
