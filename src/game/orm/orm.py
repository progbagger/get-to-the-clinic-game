from enum import Enum
from typing import List, Optional
from sqlalchemy import CheckConstraint, Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from dataclasses import dataclass

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


class Base(DeclarativeBase):
    pass


class Entity(Base):
    """Базовая сущность"""

    __abstract__ = True

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    description: Mapped[str]

    def __repr__(self):
        return f"name={self.name}, description={self.description}"


class Character(Entity):
    """Базовый класс для персонажа"""

    __abstract__ = True

    xp: Mapped[int] = mapped_column(default=BASE_XP)
    start_phrase: Mapped[str] = mapped_column(nullable=True)
    end_phrase: Mapped[str] = mapped_column(nullable=True)

    def __repr__(self):
        return f"{super().__repr__()}, xp={self.xp}"


class NPC(Character):
    """Персонаж, с которым можно взаимодействовать"""

    __tablename__ = "npcs"

    location_id: Mapped[int] = mapped_column(ForeignKey("locations.id"))
    type: Mapped[str]

    location: Mapped["Location"] = relationship(back_populates="npcs")
    items: Mapped[List["Item"]] = relationship(back_populates="npc")
    quests: Mapped[List["Quest"]] = relationship(back_populates="npc")

    __mapper_args__ = {
        "polymorphic_identity": "npc",
        "polymorphic_on": "type",
    }

    def __repr__(self):
        return f"NPC({super().__repr__()}, location={self.location.name})"


class HpStrengthMixin:
    hp: Mapped[int] = mapped_column(default=BASE_HP)
    strength: Mapped[int] = mapped_column(default=BASE_STRENGTH)


class Enemy(NPC, HpStrengthMixin):
    """Персонаж, с которым можно сражаться"""

    __tablename__ = "enemies"

    id: Mapped[int] = mapped_column(ForeignKey("npcs.id"), primary_key=True)
    phrases: Mapped[List["Phrase"]] = relationship(back_populates="enemy")

    __mapper_args__ = {"polymorphic_identity": "enemy"}

    def __repr__(self):
        return f"Enemy({super().__repr__()}, hp={self.hp}, strength={self.strength})"


class Phrase(Base):
    """Фразы для пресонажей"""

    __tablename__ = "phrases"

    id: Mapped[int] = mapped_column(primary_key=True)
    enemy_id: Mapped[int] = mapped_column(ForeignKey("enemies.id"))
    phrase: Mapped[str]

    enemy: Mapped["Enemy"] = relationship(back_populates="phrases")


class SideEffect(Entity):
    """Бафы и дебафы"""

    __tablename__ = "side_effects"

    hp_change: Mapped[int] = mapped_column(default=HP_CHANGE)
    xp_change: Mapped[int] = mapped_column(default=XP_CHANGE)
    strength_change: Mapped[int] = mapped_column(default=STRENGHT_CHANGE)

    locations: Mapped[List["Location"]] = relationship(back_populates="side_effect")
    items: Mapped[List["Item"]] = relationship(back_populates="side_effect")
    quests: Mapped[List["Quest"]] = relationship(back_populates="side_effect")

    def __repr__(self):
        return f"SideEffect({super().__repr__()})"


class Location(Entity):
    """Локации"""

    __tablename__ = "locations"

    side_effect_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("side_effects.id"), nullable=True
    )

    side_effect: Mapped["SideEffect"] = relationship(back_populates="locations")
    items: Mapped[List["Item"]] = relationship(back_populates="location")
    npcs: Mapped[List["NPC"]] = relationship(back_populates="location")

    neighbour_locations: Mapped[List["Location"]] = relationship(
        "Location",
        secondary="connected_locations",
        primaryjoin="Location.id==connected_locations.c.location_id",
        secondaryjoin="Location.id==connected_locations.c.neighbour_id",
        back_populates="neighbour_locations",
    )

    def __repr__(self):
        return f"Location({super().__repr__()})"


connected_locations = Table(
    "connected_locations",
    Base.metadata,
    Column("location_id", ForeignKey("locations.id"), primary_key=True),
    Column("neighbour_id", ForeignKey("locations.id"), primary_key=True),
)


class Quest(Entity):
    """Квест"""

    __tablename__ = "quests"

    side_effect_id: Mapped[Optional[int]] = mapped_column(ForeignKey("side_effects.id"))
    npc_id: Mapped[Optional[int]] = mapped_column(ForeignKey("npcs.id"), nullable=True)

    required_items: Mapped[List["Item"]] = relationship(
        back_populates="required_for_quest",
        foreign_keys="[Item.required_for_quest_id]",
    )
    # parent_quests: Mapped[List["Quest"]] = relationship("Quest")
    required_npcs: Mapped[List["NPC"]] = relationship(
        secondary="required_for_quest_npcs"
    )

    side_effect: Mapped["SideEffect"] = relationship(back_populates="quests")
    npc: Mapped["NPC"] = relationship(back_populates="quests", foreign_keys=[npc_id])
    reward: Mapped["Item"] = relationship(
        back_populates="reward_for_quest", foreign_keys="[Item.reward_for_quest_id]"
    )

    def __repr__(self):
        return f"Quest({super().__repr__()})"


required_for_quest_npcs = Table(
    "required_for_quest_npcs",
    Base.metadata,
    Column("quest_id", ForeignKey("quests.id"), primary_key=True),
    Column("npc_id", ForeignKey("npcs.id"), primary_key=True),
)


class Item(Entity):
    """Предмет, который может использовать персонаж"""

    __tablename__ = "items"

    side_effect_id: Mapped[Optional[int]] = mapped_column(ForeignKey("side_effects.id"))
    npc_id: Mapped[Optional[int]] = mapped_column(ForeignKey("npcs.id"), nullable=True)
    reward_for_quest_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("quests.id"), nullable=True
    )
    location_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("locations.id"), nullable=True
    )
    required_for_quest_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("quests.id")
    )

    side_effect: Mapped["SideEffect"] = relationship(back_populates="items")
    npc: Mapped["NPC"] = relationship(back_populates="items")
    reward_for_quest: Mapped["Quest"] = relationship(
        back_populates="reward", foreign_keys=reward_for_quest_id
    )
    location: Mapped["Location"] = relationship(back_populates="items")
    required_for_quest: Mapped["Quest"] = relationship(
        back_populates="required_items", foreign_keys=required_for_quest_id
    )

    __table_args__ = (
        CheckConstraint(
            "(reward_for_quest_id IS NOT NULL) + (npc_id IS NOT NULL) + (location_id IS NOT NULL) = 1",
            name="one_not_null_check",
        ),
    )

    def __repr__(self):
        return f"Item({super().__repr__()})"


# Изменяемые таблицы


class Protagonist(Character, HpStrengthMixin):
    """Протагонист"""

    __tablename__ = "protagonists"

    id: Mapped[int] = mapped_column(primary_key=True)
    location_id: Mapped[int] = mapped_column(ForeignKey("locations.id"), default=1)

    location: Mapped["Location"] = relationship()
    quests: Mapped[List["ProtagonistQuest"]] = relationship()
    items: Mapped[List["ProtagonistItems"]] = relationship()
    met_npcs: Mapped[List["Enemy"]] = relationship(secondary="met_npcs")

    def __repr__(self):
        return f"Protagonist(name={self.name}, description={self.description}, xp={self.xp}, hp={self.hp}, strength={self.strength})"


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
