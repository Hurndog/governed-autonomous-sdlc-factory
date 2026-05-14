"""Audit logging middleware."""
import time
import uuid
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from src.core.logging import get_logger

logger = get_logger("audit")


class AuditMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())
        trace_id = request.headers.get("X-Trace-ID", request_id)
        start_time = time.time()

        request.state.request_id = request_id
        request.state.trace_id = trace_id

        response: Response = await call_next(request)

        duration_ms = (time.time() - start_time) * 1000

        logger.info(
            "audit_request",
            extra={
                "request_id": request_id,
                "trace_id": trace_id,
                "method": request.method,
                "path": str(request.url.path),
                "status_code": response.status_code,
                "duration_ms": round(duration_ms, 2),
                "user_agent": request.headers.get("user-agent", ""),
                "client_ip": request.client.host if request.client else None,
            },
        )

        response.headers["X-Request-ID"] = request_id
        response.headers["X-Trace-ID"] = trace_id
        response.headers["X-Duration-Ms"] = str(round(duration_ms, 2))

        return response
