from entities import (
    BaseEntity,
    Entity,
    SideEffect,
    Item,
    BaseEnemy,
    Enemy,
    Protagonist,
    NPC,
    Quest,
    QuestStatus,
    Location,
    GameException,
    UsedItemException,
)
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker


class GameSession:
    """Скоро придумаю"""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session


class Game:
    """Объект, создающий схему базы данных и порождающий игровые сессии"""

    _session: AsyncSession | None = None

    # игровые сущности, необходимые для определения положения и характеристик игрока
    _protagonist: Protagonist
    _current_location: Location

    def __init__(self, connection_string: str) -> None:
        self._engine = create_async_engine(connection_string)

        self._session_maker = async_sessionmaker(self._engine)

    async def create_schema(self) -> None:
        """Метод для создания всех таблиц"""
        async with self._engine.begin() as conn:
            await conn.run_sync(BaseEntity.metadata.create_all)

    async def drop_schema(self) -> None:
        """Метод для удаления всех таблиц"""

    async def __aenter__(self) -> GameSession:
        self._session = self._session_maker()
        return GameSession(self._session)

    async def __aexit__(self, *args, **kwargs) -> None:
        if self._session is not None:
            self._session.close()
