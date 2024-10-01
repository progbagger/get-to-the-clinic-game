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
from sqlalchemy import select


class GameSession:
    """Скоро придумаю"""

    def __init__(
        self,
        session: AsyncSession,
        protagonist: Protagonist,
        current_location: Location,
    ) -> None:
        self._session = session

        self.protagonist = protagonist
        self.current_location = current_location

    def get_quests(self, *quest_statuses: tuple[QuestStatus]) -> list[Quest]:
        return (
            [
                quest
                for quest in self.protagonist.quests
                if quest.status in quest_statuses
            ]
            if quest_statuses
            else self.protagonist.quests
        )

    @property
    def all_quests(self) -> list[Quest]:
        return self.get_quests()

    @property
    def completed_quests(self) -> list[Quest]:
        return self.get_quests(QuestStatus.COMPLETED)

    @property
    def not_started_quests(self) -> list[Quest]:
        return self.get_quests(QuestStatus.NOT_STARTED)

    @property
    def handed_quests(self) -> list[Quest]:
        return self.get_quests(QuestStatus.HANDED)

    @property
    def started_quests(self) -> list[Quest]:
        return self.get_quests(QuestStatus.IN_PROGRESS)


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
        if self._session is None:
            self._session = self._session_maker()

        return GameSession(self._session)

    async def __aexit__(self, *args, **kwargs) -> None:
        if self._session is not None:
            self._session.close()
        self._session = None
