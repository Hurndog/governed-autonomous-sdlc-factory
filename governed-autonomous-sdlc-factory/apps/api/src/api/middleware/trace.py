"""Trace ID middleware."""
import uuid
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware


class TraceMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        trace_id = request.headers.get("X-Trace-ID", str(uuid.uuid4()))
        request.state.trace_id = trace_id

        response: Response = await call_next(request)
        response.headers["X-Trace-ID"] = trace_id
        return response
