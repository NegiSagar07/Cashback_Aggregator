import os
import asyncio

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.pool import NullPool
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.auth import get_current_user
from app.config import settings
from app.database import Base, db_session
from app.main import app
from app.models import User

TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    (
        f"postgresql+asyncpg://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}"
        f"@{'localhost' if settings.POSTGRES_HOST in {'db', 'postgres'} else settings.POSTGRES_HOST}"
        f":{os.getenv('TEST_POSTGRES_PORT', '5433') if settings.POSTGRES_HOST in {'db', 'postgres'} else settings.POSTGRES_PORT}/test_db"
    ),
)

test_engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
    future=True,
    poolclass=NullPool,
)

TestSessionLocal = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_test_database():
    try:
        async with test_engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)
    except Exception as exc:
        pytest.skip(f"Test database could not be initialized: {exc}")

    yield

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await test_engine.dispose()

@pytest_asyncio.fixture
async def async_db_session() -> AsyncSession:  # type: ignore
    async with TestSessionLocal() as session:
        yield session
        # Use truncate for fast resetting state instead of rollback or recreation
        for table in reversed(Base.metadata.sorted_tables):
            await session.execute(table.delete())
        await session.commit()

@pytest_asyncio.fixture
async def test_user(async_db_session: AsyncSession) -> User:
    user = User(username="test_user", hashed_password="not_used", is_active=True)
    async_db_session.add(user)
    await async_db_session.commit()
    await async_db_session.refresh(user)
    return user

@pytest_asyncio.fixture
async def client(async_db_session: AsyncSession, test_user: User):
    async def _override_db_session():
        yield async_db_session

    async def _override_current_user():
        return test_user

    app.dependency_overrides[db_session] = _override_db_session
    app.dependency_overrides[get_current_user] = _override_current_user

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        yield ac

    app.dependency_overrides.clear()
