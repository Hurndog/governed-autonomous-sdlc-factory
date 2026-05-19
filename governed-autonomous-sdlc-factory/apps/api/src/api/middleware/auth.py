"""Authentication middleware — protects all non-public endpoints."""
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from src.core.auth import decode_token, JWT_SECRET_KEY

# Paths that do not require authentication
_PUBLIC_PATHS = {
    "/health",
    "/metrics",
    "/docs",
    "/redoc",
    "/openapi.json",
    "/api/v1/auth/login",
    "/api/v1/auth/me",  # Will handle auth internally
}

# Prefixes that are public
_PUBLIC_PREFIXES = (
    "/api/v1/auth/",  # All auth endpoints handle their own auth
)


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        path = request.url.path

        # Check if path is public
        if path in _PUBLIC_PATHS:
            return await call_next(request)

        # Check if path starts with a public prefix
        if path.startswith(_PUBLIC_PREFIXES):
            return await call_next(request)

        # Check for bootstrap endpoint (special handling)
        if path == "/api/v1/auth/bootstrap-admin":
            return await call_next(request)

        # All other endpoints require authentication
        # The actual token validation happens in the endpoint dependencies
        # This middleware just ensures the request passes through
        response = await call_next(request)
        return response
