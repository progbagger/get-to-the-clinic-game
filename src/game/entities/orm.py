from enum import Enum, auto
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
    declared_attr,
)
from sqlalchemy import ForeignKey, JSON
from sqlalchemy.ext.asyncio import AsyncAttrs
from typing import Optional

BASE_XP: int = 0
BASE_HP: int = 10
BASE_STRENGTH: int = 1

BASE_XP_CHANGE: int = 1
BASE_HP_CHANGE: int = 1
BASE_STRENGTH_CHANGE: int = 1

BASE_VALUE: int = 0


class GameException(Exception):
    pass


class UsedItemException(GameException):
    pass


class Base(AsyncAttrs, DeclarativeBase):
    pass


class BaseEntity(Base):
    __abstract__ = True

    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str]
    description: Mapped[str]

    def __repr__(self) -> str:
        return f'name="{self.name}", description="{self.description}"'


class Entity(BaseEntity):
    __abstract__ = True

    xp: Mapped[int] = mapped_column(default=BASE_XP)
    start_phrase: Mapped[str]
    end_phrase: Mapped[str]
    middle_phrases: Mapped[list[str]] = mapped_column(JSON, default=list)
    item_ids: Mapped[list[int]] = mapped_column(
        ForeignKey("item.id"), type_=JSON, default=list
    )

    @declared_attr
    def items(cls) -> Mapped[list["Item"]]:
        return relationship("Item", foreign_keys=[cls.item_ids], uselist=True)

    def __repr__(self) -> str:
        return f'{super().__repr__()}, xp={self.xp}, start_phrase="{self.start_phrase}", end_phrase="{self.end_phrase}", middle_phrases={repr(self.middle_phrases)}, items={repr(self.items)}'


class SideEffect(BaseEntity):
    __tablename__ = "side_effect"

    hp_change: Mapped[int] = mapped_column(default=BASE_HP_CHANGE)
    xp_change: Mapped[int] = mapped_column(default=BASE_XP_CHANGE)
    strength_change: Mapped[int] = mapped_column(default=BASE_STRENGTH_CHANGE)
    item_ids: Mapped[list[int]] = mapped_column(
        ForeignKey("item.id"), type_=JSON, default=list
    )

    @declared_attr
    def items(cls) -> Mapped[list["Item"]]:
        return relationship("Item", foreign_keys=[cls.item_ids], uselist=True)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}{{{super().__repr__()}, hp_change={self.hp_change}, xp_change={self.xp_change}, strength_change={self.strength_change}, items={repr(self.items)}}}"


class Item(BaseEntity):
    __tablename__ = "item"

    value: Mapped[int] = mapped_column(default=BASE_VALUE)
    side_effect_id: Mapped[Optional[int]] = mapped_column(ForeignKey("side_effect.id"))
    side_effect: Mapped[Optional[SideEffect]] = relationship(
        foreign_keys=[side_effect_id]
    )
    use_count: Mapped[Optional[int]] = mapped_column(default=None)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}{{{super().__repr__()}, value={self.value}, side_effect={repr(self.side_effect)}, use_count={self.use_count}}}"

    def use(self, enemy: "Enemy") -> None:
        if self.use_count is not None:
            if self.use_count == 0:
                raise UsedItemException(f'Предмет "{self.name}" уже использован')
            self.use_count -= 1

        enemy.hp += self.side_effect.hp_change
        enemy.strength += self.side_effect.strength_change
        enemy.xp += self.side_effect.xp_change


class Enemy(Entity):
    __tablename__ = "enemy"
    __allow_unmapped__ = True

    hp: Mapped[int] = mapped_column(default=BASE_HP)
    strength: Mapped[int] = mapped_column(default=BASE_STRENGTH)

    xp_change: int = 0

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}{{{super().__repr__()}, hp={self.hp}, strength={self.strength}}}"

    def heal(self, amount: int = 1) -> None:
        if self.hp + amount > 10:
            self.hp = 10
        else:
            self.hp += amount

    def take_hit(self, amount: int = 1) -> None:
        if amount < 0:
            self.heal(-amount)
        else:
            self.hp -= amount

    @property
    def current_level(self) -> int:
        # TODO: Придумать систему уровней на основе XP
        pass

    def level_up(self) -> int:
        pass

    def attack(self, *, enemy: "Enemy", amount: int = 1) -> None:
        enemy.take_hit(amount)


class NPC(Entity):
    __tablename__ = "npc"

    quest_ids: Mapped[list[int]] = mapped_column(
        ForeignKey("quest.id"), type_=JSON, default=list
    )

    @declared_attr
    def quests(cls) -> Mapped[list["Quest"]]:
        return relationship("Quest", foreign_keys=[cls.quest_ids], uselist=True)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}{{{super().__repr__()}, quests={repr(self.quests)}}}"

    def take_quests(self) -> list["Quest"]:
        result = self.quests
        self.quests.clear()
        self.quest_ids.clear()

        return result


class Protagonist(Entity):
    __tablename__ = "protagonist"

    quest_ids: Mapped[list[int]] = mapped_column(
        ForeignKey("quest.id"), type_=JSON, default=list
    )

    @declared_attr
    def quests(cls) -> Mapped[list["Quest"]]:
        return relationship("Quest", foreign_keys=[cls.quest_ids], uselist=True)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}{{{super().__repr__()}, quests={repr(self.quests)}}}"

    def talk_to(self, npc: NPC) -> list["Quest"]:
        new_quests = npc.take_quests()

        self.quests.extend(new_quests)
        self.quest_ids.extend([quest.id for quest in new_quests])

        return new_quests


class QuestStatus(Enum):
    NOT_STARTED = auto()
    IN_PROGRESS = auto()
    COMPLETED = auto()
    HANDED = auto()


class Quest(BaseEntity):
    __tablename__ = "quest"

    required_enemy_ids: Mapped[list[int]] = mapped_column(
        ForeignKey("enemy.id"), type_=JSON, default=list
    )
    required_enemies: Mapped[list[Enemy]] = relationship(
        foreign_keys=[required_enemy_ids], uselist=True
    )

    required_npc_ids: Mapped[list[int]] = mapped_column(
        ForeignKey("npc.id"), type_=JSON, default=list
    )
    required_npcs: Mapped[list[NPC]] = relationship(
        foreign_keys=[required_npc_ids], uselist=True
    )

    required_item_ids: Mapped[list[int]] = mapped_column(
        ForeignKey("item.id"), type_=JSON, default=list
    )
    required_items: Mapped[list[Item]] = relationship(
        foreign_keys=[required_item_ids], uselist=True
    )

    reward_id: Mapped[int] = mapped_column(ForeignKey("side_effect.id"))
    reward: Mapped[SideEffect] = relationship(foreign_keys=[reward_id])

    status: Mapped[QuestStatus]

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}{{{super().__repr__()}, required_enemies={repr(self.required_enemies)}, required_npcs={repr(self.required_npcs)}, required_items={repr(self.required_items)}, reward={repr(self.reward)}, status={repr(self.status)}}}"


class Location(BaseEntity):
    __tablename__ = "location"

    location_ids: Mapped[list[int]] = mapped_column(
        ForeignKey("location.id"), type_=JSON, default=list
    )

    @declared_attr
    def locations(cls) -> Mapped[list["Location"]]:
        return relationship("Location", foreign_keys=[cls.location_ids], uselist=True)

    npc_ids: Mapped[list[int]] = mapped_column(
        ForeignKey("npc.id"), type_=JSON, default=list
    )
    npcs: Mapped[list[NPC]] = relationship(foreign_keys=npc_ids, uselist=True)

    enemy_ids: Mapped[list[int]] = mapped_column(
        ForeignKey("enemy.id"), type_=JSON, default=list
    )
    enemies: Mapped[list[Enemy]] = relationship(foreign_keys=[enemy_ids], uselist=True)

    side_effect_id: Mapped[Optional[int]] = mapped_column(ForeignKey("side_effect.id"))
    side_effect: Mapped[Optional[SideEffect]] = relationship(
        foreign_keys=[side_effect_id]
    )

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}{{{super().__repr__()}, location_ids={repr(self.location_ids)}, npcs={repr(self.npcs)}, enemies={repr(self.enemies)}, side_effect={repr(self.side_effect)}}}"


if __name__ == "__main__":
    """Тест работы таблиц"""

    from sqlalchemy import create_engine
    from sqlalchemy.orm import Session

    connection_str = "sqlite:///:memory:"
    engine = create_engine(connection_str, echo=True)
    BaseEntity.metadata.create_all(bind=engine)

    with Session(bind=engine) as session:
        protagonist = Protagonist(
            name="Sus",
            description="Amogus",
            start_phrase="Yahoo!",
            end_phrase="Sheesh!",
            items=[
                Item(
                    name="Sword",
                    description="An iron sword",
                    side_effect=SideEffect(
                        name="Aaarrrggghhh!",
                        description="Some effect",
                        strength_change=1,
                    ),
                ),
                Item(
                    name="Shield",
                    description="A wooden shield",
                    side_effect=SideEffect(
                        name="Protection", description="Some effect", hp_change=1
                    ),
                ),
            ],
            quests=[
                Quest(
                    name="More power!",
                    description="We need more power!",
                    status=QuestStatus.NOT_STARTED,
                    reward=SideEffect(
                        name="Quest reward",
                        description="Quest reward",
                        items=[
                            Item(
                                name="Apple",
                                description="It heals you",
                                side_effect=SideEffect(
                                    name="Heal", description="Heal", hp_change=1
                                ),
                            )
                        ],
                    ),
                    required_npcs=[
                        NPC(
                            name="Babushka",
                            description="She is an old woman",
                            start_phrase="Hi there!",
                            end_phrase="Bye!",
                        )
                    ],
                    required_enemies=[
                        Enemy(
                            name="Another babushka",
                            description="Uuugh!",
                            start_phrase="I am an old woman! Respect me!",
                            end_phrase="My back!",
                        )
                    ],
                )
            ],
        )
        location = Location(
            name="Hall",
            description="The place where everything is started",
        )

        session.add(protagonist)
        session.add(location)
        session.commit()

        print(session.query(Item).all())
        print(session.query(Location).all())
