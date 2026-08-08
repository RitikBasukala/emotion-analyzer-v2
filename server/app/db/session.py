"""Async PostgreSQL engine/session management (asyncpg driver).

Per architecture rules: all database I/O in this project is non-blocking.
No sync `psycopg2`/blocking driver is used anywhere.
"""

import logging
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings

logger = logging.getLogger(__name__)

engine = create_async_engine(
    settings.database_url,
    echo=False,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    future=True,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    autoflush=False,
    class_=AsyncSession,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency yielding a transactional async DB session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            logger.exception("db.session.rollback")
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_models() -> None:
    """Create tables if they do not exist yet.

    This project uses a lightweight startup `create_all` instead of a full
    Alembic migration chain to keep the local/dev loop simple. For a
    multi-environment production rollout, swap this for Alembic revisions
    without changing any calling code (it is isolated to this one function).
    """
    from app.db import models  # noqa: F401  (ensure models are registered)
    from app.db.base import Base

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("db.init_models.complete")


async def dispose_engine() -> None:
    """Cleanly dispose of the async engine's connection pool on shutdown."""
    await engine.dispose()
    logger.info("db.engine.disposed")
