"""Synchronous database engine for the replay runtime.

This module provides a completely independent sync SQLAlchemy engine
and session factory for the deterministic replay runtime.

Key design decisions:
- Uses psycopg2 (sync) driver instead of asyncpg
- Completely separate engine from the async main engine
- autoflush=False for deterministic flush timing
- No connection to FastAPI dependency injection
- No greenlet/event loop dependencies
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.core.config import settings


def _sync_url(async_url: str) -> str:
    """Convert async database URL to sync driver URL.
    
    postgresql+asyncpg://... → postgresql+psycopg2://...
    postgresql+aiosqlite://... → sqlite://...
    """
    url = async_url
    url = url.replace("postgresql+asyncpg", "postgresql+psycopg2")
    url = url.replace("postgresql+aiosqlite", "sqlite")
    return url


SYNC_DATABASE_URL = _sync_url(settings.database_url)

sync_engine = create_engine(
    SYNC_DATABASE_URL,
    future=True,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
)

SyncSessionLocal = sessionmaker(
    bind=sync_engine,
    autoflush=False,
    autocommit=False,
)
