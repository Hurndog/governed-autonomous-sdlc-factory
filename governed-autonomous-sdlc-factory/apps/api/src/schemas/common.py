"""Common Pydantic schemas."""
from typing import Optional, Generic, TypeVar, List, Any
from pydantic import BaseModel, Field

T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int = 1
    page_size: int = 50
    has_next: bool = False
    has_prev: bool = False


class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None
    request_id: Optional[str] = None
    trace_id: Optional[str] = None


class HealthResponse(BaseModel):
    status: str = "ok"
    version: str = "1.0.0"
    database: str = "connected"
    redis: str = "connected"
    uptime_seconds: float = 0.0


class MessageResponse(BaseModel):
    message: str
