"""Database engine and session management."""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from src.core.config import settings
from src.models import Base

engine = create_async_engine(
    settings.database_url,
    echo=False,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
)

async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


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
