from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from functools import wraps
from contextlib import asynccontextmanager

connection_string = "sqlite+aiosqlite:///db.db"
engine = create_async_engine(
    connection_string,
    echo=True,
)
async_session = async_sessionmaker(engine, expire_on_commit=False)


@asynccontextmanager
async def create_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session
