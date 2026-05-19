"""Database engine and session management."""
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker
from src.core.config import settings
from src.models import Base

_is_sqlite = "sqlite" in settings.database_url

_engine_kwargs: dict = {"echo": False, "pool_pre_ping": True}
if not _is_sqlite:
    _engine_kwargs["pool_size"] = 10
    _engine_kwargs["max_overflow"] = 20

engine = create_async_engine(settings.database_url, **_engine_kwargs)

async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Sync engine for operations that require synchronous SQLAlchemy (integrity, semantic coverage)
_sync_url = settings.database_url.replace("postgresql+asyncpg://", "postgresql+psycopg2://").replace("postgresql+asyncpg", "postgresql+psycopg2")
_sync_engine_kwargs: dict = {"echo": False, "pool_pre_ping": True}
if "sqlite" not in _sync_url:
    _sync_engine_kwargs["pool_size"] = 5
    _sync_engine_kwargs["max_overflow"] = 10
sync_engine = create_engine(_sync_url, **_sync_engine_kwargs)
SyncSessionLocal = sessionmaker(bind=sync_engine, expire_on_commit=False)


def init_sync_db():
    """Run sync database migrations (for sync engine startup)."""
    from sqlalchemy import text
    with sync_engine.begin() as conn:
        # Migration: add workspace_id to projects if not exists
        try:
            conn.execute(text(
                "ALTER TABLE projects ADD COLUMN IF NOT EXISTS workspace_id VARCHAR(36) REFERENCES workspaces(id)"
            ))
        except Exception:
            pass
        # Migration: add workspace_id to runs if not exists
        try:
            conn.execute(text(
                "ALTER TABLE runs ADD COLUMN IF NOT EXISTS workspace_id VARCHAR(36) REFERENCES workspaces(id)"
            ))
        except Exception:
            pass


async def get_db() -> AsyncSession:
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def get_db_no_autoflush() -> AsyncSession:
    """Get a session for replay operations. Autoflush is NOT disabled — 
    instead, the ReplayRuntime manages its own session via async_session_factory."""
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        # Migration: make task_id nullable and drop FK constraint if exists
        try:
            from sqlalchemy import text
            await conn.execute(text(
                "ALTER TABLE artifacts ALTER COLUMN task_id DROP NOT NULL"
            ))
        except Exception:
            pass  # Column may already be nullable
        try:
            from sqlalchemy import text
            await conn.execute(text(
                "ALTER TABLE artifacts DROP CONSTRAINT IF EXISTS artifacts_task_id_fkey"
            ))
        except Exception:
            pass  # Constraint may not exist
        # Migration: add workspace_id to projects if not exists
        try:
            from sqlalchemy import text
            await conn.execute(text(
                "ALTER TABLE projects ADD COLUMN IF NOT EXISTS workspace_id VARCHAR(36) REFERENCES workspaces(id)"
            ))
        except Exception:
            pass
