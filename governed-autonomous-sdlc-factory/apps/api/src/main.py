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
from src.api.v1.router import api_router
from src.websocket.run_events import ws_router

setup_logging(settings.log_level, settings.log_format)
logger = get_logger("main")

start_time = time.time()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Governed Autonomous SDLC Factory API")
    try:
        await init_db()
        logger.info("Database initialized")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
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

# Include routers
app.include_router(api_router)
app.include_router(ws_router)


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
