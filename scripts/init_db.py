"""Database initialization script — creates all tables directly from models.

Usage: python scripts/init_db.py
"""
import asyncio
import sys
import os

# Add api to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "governed-autonomous-sdlc-factory", "apps", "api"))

from src.core.config import settings
from src.core.database import engine, init_db
from src.core.logging import setup_logging, get_logger

setup_logging("INFO", "text")
logger = get_logger("init_db")


async def main():
    logger.info(f"Connecting to: {settings.database_url.replace('forge', '***')}")
    try:
        await init_db()
        logger.info("All tables created successfully.")
    except Exception as e:
        logger.error(f"Failed to create tables: {e}")
        raise
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
