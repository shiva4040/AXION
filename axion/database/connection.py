import os
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from axion.config import settings

Base = declarative_base()

# Async Engine
# Handles both PostgreSQL (postgresql+asyncpg://...) and SQLite (sqlite+aiosqlite:///...)
db_url = settings.database_url
connect_args = {}
if "sqlite" in db_url:
    connect_args = {"check_same_thread": False}

engine = create_async_engine(
    db_url,
    echo=(settings.log_level.upper() == "DEBUG"),
    future=True,
    connect_args=connect_args
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False
)

async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for providing asynchronous database sessions."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

async def init_db():
    """Initializes database schema and extensions."""
    async with engine.begin() as conn:
        # In PostgreSQL, create vector extension if pgvector is installed
        if "postgresql" in settings.database_url:
            from sqlalchemy import text
            await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
            await conn.execute(text('CREATE EXTENSION IF NOT EXISTS "uuid-ossp";'))
        
        # Create all tables defined in models
        await conn.run_sync(Base.metadata.create_all)
