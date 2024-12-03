from enum import Enum
from typing import List, Optional
from sqlalchemy import CheckConstraint, Column, ForeignKey, Table
from sqlalchemy.orm import (
    MappedAsDataclass,
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
)

BASE_XP = 0
BASE_HP = 10
BASE_STRENGTH = 10
XP_CHANGE = 0
HP_CHANGE = 0
STRENGHT_CHANGE = 0


class Status(Enum):
    NotStarted = 0
    InProgress = 1
    Comleted = 2


class Base(MappedAsDataclass, DeclarativeBase):
    pass


class Entity(Base, kw_only=True):
    """Базовая сущность"""

    __abstract__ = True

    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    name: Mapped[str]
    description: Mapped[str]


class Character(Entity, kw_only=True):
    """Базовый класс для персонажа"""

    __abstract__ = True

    xp: Mapped[int] = mapped_column(default=BASE_XP)
    start_phrase: Mapped[str]
    end_phrase: Mapped[str]


class NPC(Character, kw_only=True):
    """Персонаж, с которым можно взаимодействовать"""

    __tablename__ = "npcs"
    type: Mapped[str] = mapped_column(init=False)
    location_id: Mapped[int] = mapped_column(ForeignKey("locations.id"), init=False)
    location: Mapped["Location"] = relationship(back_populates="npcs", default=None)
    items: Mapped[List["Item"]] = relationship(
        back_populates="npc",
        default_factory=list,
    )
    quests: Mapped[List["Quest"]] = relationship(
        back_populates="npc",
        default_factory=list,
    )

    __mapper_args__ = {
        "polymorphic_identity": "npc",
        "polymorphic_on": "type",
    }


class HpStrengthMixin(MappedAsDataclass, kw_only=True):
    hp: Mapped[int] = mapped_column(default=BASE_HP)
    strength: Mapped[int] = mapped_column(default=BASE_STRENGTH)


class Enemy(HpStrengthMixin, NPC, kw_only=True):
    """Персонаж, с которым можно сражаться"""

    __tablename__ = "enemies"

    id: Mapped[int] = mapped_column(ForeignKey("npcs.id"), primary_key=True, init=False)
    phrases: Mapped[List["Phrase"]] = relationship(
        back_populates="enemy", default_factory=list
    )

    __mapper_args__ = {"polymorphic_identity": "enemy"}


class Phrase(Base, kw_only=True):
    """Фразы для пресонажей"""

    __tablename__ = "phrases"

    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    phrase: Mapped[str]
    enemy_id: Mapped[int] = mapped_column(ForeignKey("enemies.id"), init=False)
    enemy: Mapped["Enemy"] = relationship(back_populates="phrases", default=None)


class SideEffect(Entity, kw_only=True):
    """Бафы и дебафы"""

    __tablename__ = "side_effects"

    hp_change: Mapped[int] = mapped_column(default=HP_CHANGE)
    xp_change: Mapped[int] = mapped_column(default=XP_CHANGE)
    strength_change: Mapped[int] = mapped_column(default=STRENGHT_CHANGE)

    locations: Mapped[List["Location"]] = relationship(
        back_populates="side_effect", default_factory=list
    )
    items: Mapped[List["Item"]] = relationship(
        back_populates="side_effect", default_factory=list
    )
    quests: Mapped[List["Quest"]] = relationship(
        back_populates="side_effect", default_factory=list
    )


class Location(Entity, kw_only=True):
    """Локации"""

    __tablename__ = "locations"

    side_effect_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("side_effects.id"), nullable=True, init=False
    )

    side_effect: Mapped["SideEffect"] = relationship(
        back_populates="locations", default=None
    )

    items: Mapped[List["Item"]] = relationship(
        back_populates="location", default_factory=list
    )
    npcs: Mapped[List["NPC"]] = relationship(
        back_populates="location", default_factory=list
    )

    neighbour_locations: Mapped[List["Location"]] = relationship(
        "Location",
        secondary="connected_locations",
        primaryjoin="Location.id==connected_locations.c.location_id",
        secondaryjoin="Location.id==connected_locations.c.neighbour_id",
        back_populates="neighbour_locations",
        default_factory=list,
    )


connected_locations = Table(
    "connected_locations",
    Base.metadata,
    Column("location_id", ForeignKey("locations.id"), primary_key=True),
    Column("neighbour_id", ForeignKey("locations.id"), primary_key=True),
)


class Quest(Entity, kw_only=True):
    """Квест"""

    __tablename__ = "quests"

    side_effect_id: Mapped[int] = mapped_column(
        ForeignKey("side_effects.id"), init=False
    )
    npc_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("npcs.id"),
        nullable=True,
        init=False,
    )

    required_items: Mapped[List["Item"]] = relationship(
        back_populates="required_for_quest",
        foreign_keys="[Item.required_for_quest_id]",
        default_factory=list,
    )
    required_quests: Mapped[List["Quest"]] = relationship(
        "Quest",
        secondary="required_quests",
        primaryjoin="Quest.id==required_quests.c.parent_quest_id",
        secondaryjoin="Quest.id==required_quests.c.child_quest_id",
        back_populates="required_quests",
        default_factory=list,
    )

    required_npcs: Mapped[List["NPC"]] = relationship(
        secondary="required_for_quest_npcs",
        default_factory=list,
    )

    side_effect: Mapped["SideEffect"] = relationship(
        back_populates="quests", default=None
    )

    npc: Mapped["NPC"] = relationship(
        back_populates="quests", foreign_keys=[npc_id], default=None
    )

    reward: Mapped[Optional["Item"]] = relationship(
        back_populates="reward_for_quest",
        foreign_keys="[Item.reward_for_quest_id]",
        default=None,
    )


required_quests = Table(
    "required_quests",
    Base.metadata,
    Column("parent_quest_id", ForeignKey("quests.id"), primary_key=True),
    Column("child_quest_id", ForeignKey("quests.id"), primary_key=True),
)


required_for_quest_npcs = Table(
    "required_for_quest_npcs",
    Base.metadata,
    Column("quest_id", ForeignKey("quests.id"), primary_key=True),
    Column("npc_id", ForeignKey("npcs.id"), primary_key=True),
)


class Item(Entity, kw_only=True):
    """Предмет, который может использовать персонаж"""

    __tablename__ = "items"

    side_effect_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("side_effects.id"), nullable=True, init=False
    )
    npc_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("npcs.id"), nullable=True, init=False
    )
    reward_for_quest_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("quests.id"), nullable=True, init=False
    )
    location_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("locations.id"), nullable=True, init=False
    )
    required_for_quest_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("quests.id"), nullable=True, init=False
    )

    side_effect: Mapped["SideEffect"] = relationship(
        back_populates="items", default=None
    )
    npc: Mapped["NPC"] = relationship(back_populates="items", default=None)
    location: Mapped["Location"] = relationship(back_populates="items", default=None)

    reward_for_quest: Mapped["Quest"] = relationship(
        back_populates="reward", foreign_keys=reward_for_quest_id, default=None
    )
    required_for_quest: Mapped["Quest"] = relationship(
        back_populates="required_items",
        foreign_keys=required_for_quest_id,
        default=None,
    )

    __table_args__ = (
        CheckConstraint(
            "(reward_for_quest_id IS NOT NULL) + (npc_id IS NOT NULL) + (location_id IS NOT NULL) = 1",
            name="one_not_null_check",
        ),
    )


# Изменяемые таблицы


class Protagonist(HpStrengthMixin, Character, kw_only=True):
    """Протагонист"""

    __tablename__ = "protagonists"

    id: Mapped[int] = mapped_column(primary_key=True)
    location_id: Mapped[int] = mapped_column(ForeignKey("locations.id"), init=False)

    location: Mapped["Location"] = relationship()
    quests: Mapped[List["ProtagonistQuest"]] = relationship(default_factory=list)
    items: Mapped[List["ProtagonistItems"]] = relationship(default_factory=list)
    met_npcs: Mapped[List["NPC"]] = relationship(
        secondary="met_npcs", default_factory=list
    )


met_npcs = Table(
    "met_npcs",
    Base.metadata,
    Column("protagonist_id", ForeignKey("protagonists.id"), primary_key=True),
    Column("npc_id", ForeignKey("npcs.id"), primary_key=True),
)


class ProtagonistQuest(Base):
    """Квесты, которые взял протагонист и их статус"""

    __tablename__ = "protagonist_quests"

    protagonist_id: Mapped[int] = mapped_column(
        ForeignKey("protagonists.id"), primary_key=True
    )

    quest_id: Mapped[int] = mapped_column(ForeignKey("quests.id"), primary_key=True)
    status: Mapped["Status"]
    quest: Mapped["Quest"] = relationship()


class ProtagonistItems(Base):
    """Все предметы, которые есть у протагониста (использованные и нет)"""

    __tablename__ = "protagonist_items"

    protagonist_id: Mapped[int] = mapped_column(
        ForeignKey("protagonists.id"), primary_key=True
    )
    item_id: Mapped[int] = mapped_column(ForeignKey("items.id"), primary_key=True)
    used: Mapped[bool]

    item: Mapped["Item"] = relationship()
