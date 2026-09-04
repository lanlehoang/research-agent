"""Async SQLAlchemy setup for PostgreSQL + pgvector."""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from research_agent.utils.config import settings

engine = create_async_engine(
    settings.postgres_url,
    echo=False,
    future=True,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db():
    """Yield an async session for dependency injection."""
    async with AsyncSessionLocal() as session:
        yield session
