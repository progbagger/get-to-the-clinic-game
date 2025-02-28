from typing import AsyncGenerator
from sqlalchemy.orm import DeclarativeBase, MappedAsDataclass
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession,
    AsyncAttrs,
)
from contextlib import asynccontextmanager


class Base(AsyncAttrs, DeclarativeBase, MappedAsDataclass):
    pass


class DatabaseManager:

    def __init__(self, database_url: str = "sqlite+aiosqlite:///db.db") -> None:
        """Инициализация асинхронного движка и фабрики сессий"""

        self.engine = create_async_engine(database_url, echo=True)
        self.async_session = async_sessionmaker(self.engine, expire_on_commit=False)

    async def create_tables(self) -> None:
        """Создание всех таблиц в базе данных"""

        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def drop_tables(self) -> None:
        """Удаление всех таблиц из базы данных"""

        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)

    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        async with self.async_session() as session:
            yield session


db_manager = DatabaseManager()

test_db_manager = DatabaseManager("sqlite+aiosqlite:///:memory:")
