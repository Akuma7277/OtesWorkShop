from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)



def create_session_pool(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    """
    Creates a session pool.
    """
    return async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

async def get_session(session_pool: async_sessionmaker[AsyncSession]) -> AsyncGenerator[AsyncSession, None]:
    """
    Provides a database session from the session pool.
    """
    async with session_pool() as session:
        yield session
