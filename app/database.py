from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    create_async_engine,
    async_sessionmaker,
)
from typing import AsyncGenerator
from sqlalchemy.orm import DeclarativeBase
from .config import settings


class Base(DeclarativeBase):
    """Base registry for all database models."""
    pass

# We trust that settings.DATABASE_URL is already validated by Pydantic
DATABASE_URL = settings.DATABASE_URL 

engine: AsyncEngine = create_async_engine(DATABASE_URL, echo=True) #echo=True for logging SQL queries, can be turned off in production

AsyncSessionLocal = async_sessionmaker(
    engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False # improve performance in async fastapi apps
)

async def db_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session