from enum import Enum
from typing import Optional, Union
from sqlalchemy import CheckConstraint, Column, ForeignKey, Table, select
from sqlalchemy.orm import (
    MappedAsDataclass,
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
    selectin_polymorphic,
    joinedload,
    selectinload,
)
from sqlalchemy.ext.asyncio import AsyncAttrs
from get_to_the_clinic_game.orm.database import create_session


BASE_XP = 0
BASE_HP = 10
BASE_STRENGTH = 10
XP_CHANGE = 0
HP_CHANGE = 0
STRENGHT_CHANGE = 0


class Status(Enum):
    NotStarted = 0
    InProgress = 1
    Completed = 2


class Base(MappedAsDataclass, AsyncAttrs, DeclarativeBase):
    pass


class Entity(Base, kw_only=True):
    """Базовая сущность"""

    __abstract__ = True

    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    name: Mapped[str]
    description: Mapped[str]


class BaseCharacter(Entity, kw_only=True):
    """Базовый класс для персонажа"""

    __abstract__ = True

    start_phrase: Mapped[str]
    end_phrase: Mapped[str]
    xp: Mapped[int] = mapped_column(default=BASE_XP)


class Character(BaseCharacter, kw_only=True):
    """Класс для NPC и Enemy"""

    __tablename__ = "characters"

    location_id: Mapped[int] = mapped_column(ForeignKey("locations.id"), init=False)
    type: Mapped[str] = mapped_column(init=False)

    location: Mapped["Location"] = relationship(
        back_populates="characters",
        default=None,
        lazy=None,
    )

    __mapper_args__ = {
        "polymorphic_identity": "character",
        "polymorphic_on": "type",
    }

    @staticmethod
    async def get_full_character_info(
        character_id: int, protagonist_id: int
    ) -> Union["Enemy", "NPC"]:
        async with create_session() as session:

            character: NPC | Enemy = await session.scalar(
                select(Character)
                .filter(Character.id == character_id)
                .options(
                    selectin_polymorphic(Character, [NPC, Enemy]),
                )
            )
            # if character == "npc":

            #     # отфильтровать квесты, которые есть уже взял протагониста

            #     character.quests = [
            #         quest
            #         for quest in character.quests
            #         if quest.id not in protagonist_quests
            #     ]
            return character


class NPC(Character, kw_only=True):
    """Персонаж, с которым можно взаимодействовать"""

    __tablename__ = "npcs"

    id: Mapped[int] = mapped_column(
        ForeignKey("characters.id"),
        primary_key=True,
        init=False,
    )

    quests: Mapped[list["Quest"]] = relationship(
        back_populates="npc",
        default_factory=list,
        lazy=None,
    )

    __mapper_args__ = {"polymorphic_identity": "npc"}

    @staticmethod
    async def get_all_npc_quest(npc_id: int) -> list["Quest"]:
        async with create_session() as session:
            quests = (
                await session.scalars((select(Quest).filter(Quest.npc_id == npc_id)))
            ).all()

            return quests


class HpStrengthMixin(MappedAsDataclass, kw_only=True):
    hp: Mapped[int] = mapped_column(default=BASE_HP)
    strength: Mapped[int] = mapped_column(default=BASE_STRENGTH)


class Enemy(HpStrengthMixin, Character, kw_only=True):
    """Персонаж, с которым можно сражаться"""

    __tablename__ = "enemies"

    id: Mapped[int] = mapped_column(
        ForeignKey("characters.id"),
        primary_key=True,
        init=False,
    )

    phrases: Mapped[list["Phrase"]] = relationship(
        back_populates="enemy",
        default_factory=list,
        lazy=None,
    )

    items: Mapped[list["Item"]] = relationship(
        back_populates="enemy",
        default_factory=list,
        lazy=None,
    )

    __mapper_args__ = {"polymorphic_identity": "enemy"}

    async def attack():
        pass


class Phrase(Base, kw_only=True):
    """Фразы для пресонажей"""

    __tablename__ = "phrases"

    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    phrase: Mapped[str]

    enemy_id: Mapped[int] = mapped_column(
        ForeignKey("enemies.id"),
        init=False,
    )

    enemy: Mapped["Enemy"] = relationship(
        back_populates="phrases",
        default=None,
        lazy=None,
    )


class SideEffect(Entity, kw_only=True):
    """Бафы и дебафы"""

    __tablename__ = "side_effects"

    hp_change: Mapped[int] = mapped_column(default=HP_CHANGE)
    xp_change: Mapped[int] = mapped_column(default=XP_CHANGE)
    strength_change: Mapped[int] = mapped_column(default=STRENGHT_CHANGE)

    def __repr__(self):
        res = f"{self.description} ("

        if self.hp_change:
            res += f"{self.hp_change} hp "

        if self.xp_change:
            res += f"{self.xp_change} xp "

        if self.strength_change:
            res += f"{self.strength_change} силы"

        return res + ")"

    # async def apply(self, *, character: Union["Protagonist", "Enemy"]) -> None:
    #     async with create_session() as session:
    #         character.hp += self.hp_change
    #         character.xp += self.hp_change
    #         character.strength += self.hp_change
    #         if isinstance(character, Protagonist):
    #             character.apllied_side_effect.add(self.id)
    #             session.commit()

    # async def cancel(self, *, character: Union["Protagonist", "Enemy"]) -> None:
    #     async with create_session() as session:
    #         character.hp -= self.hp_change
    #         character.xp -= self.hp_change
    #         character.strength -= self.hp_change
    #         if isinstance(character, Protagonist):
    #             character.apllied_side_effect.remove(self.id)
    #             session.commit()


class Location(Entity, kw_only=True):
    """Локации"""

    __tablename__ = "locations"

    side_effect_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("side_effects.id"),
        nullable=True,
        init=False,
    )

    side_effect: Mapped["SideEffect"] = relationship(
        default=None,
        lazy=None,
    )

    items: Mapped[list["Item"]] = relationship(
        back_populates="location",
        default_factory=list,
        lazy=None,
    )

    characters: Mapped[list["Character"]] = relationship(
        back_populates="location",
        default_factory=list,
        lazy=None,
    )

    neighbour_locations: Mapped[list["Location"]] = relationship(
        "Location",
        secondary="connected_locations",
        primaryjoin="Location.id==connected_locations.c.location_id",
        secondaryjoin="Location.id==connected_locations.c.neighbour_id",
        back_populates="neighbour_locations",
        default_factory=list,
        lazy=None,
    )

    def __repr__(self):
        result = f"{self.name}\nОписание: {self.description}"
        result += f"\nЭффект локации: {self.side_effect}"
        result += "\nПерсонажи: " + ", ".join(
            [f"{character.name} ({character.type})" for character in self.characters]
        )

        result += "\nПредметы: " + ", ".join([f"{item.name}" for item in self.items])
        result += "\nСоседнии локации: " + ", ".join(
            [f"{location.name}" for location in self.neighbour_locations]
        )
        return result

    @staticmethod
    async def get_full_info_location(
        location_id: int, protagonist_id: int
    ) -> "Location":
        async with create_session() as session:

            subquery1 = (
                select(defeated_enemies.c.enemy_id)
                .where(defeated_enemies.c.protagonist_id == protagonist_id)
                .scalar_subquery()
            )

            subquery2 = (
                select(ProtagonistItems.item_id)
                .where(ProtagonistItems.protagonist_id == protagonist_id)
                .scalar_subquery()
            )

            query = (
                select(Location)
                .options(joinedload(Location.characters))
                .options(joinedload(Location.items))
                .options(joinedload(Location.neighbour_locations))
                .where(~Character.id.in_(subquery1))
                .where(~Item.id.in_(subquery2))
                .where(Location.id == location_id)
            )

            location: Location = await session.scalar(query)
            return location

    @staticmethod
    async def get_neighbour_locations(location_id: int) -> list["Location"]:
        async with create_session() as session:
            query = (
                select(Location)
                .join(
                    connected_locations,
                    Location.id == connected_locations.c.location_id,
                )
                .where(connected_locations.c.neighbour_id == location_id)
            )
            neighbours = (await session.scalars(query)).all()
            return neighbours

    @staticmethod
    async def get_all_characters_on_location(
        location_id: int, protagonist_id: int
    ) -> list["Character"]:
        async with create_session() as session:
            subquery = (
                select(defeated_enemies.c.enemy_id)
                .where(defeated_enemies.c.protagonist_id == protagonist_id)
                .scalar_subquery()
            )

            query = (
                select(Character)
                .where(Character.location_id == location_id)
                .where(Character.id.not_in(subquery))
            )
            characters = (await session.scalars(query)).all()

            return characters

    @staticmethod
    async def get_all_items_on_location(
        location_id: int, protagonist_id: int
    ) -> list["Item"]:
        async with create_session() as session:
            subquery = (
                select(ProtagonistItems.item_id)
                .where(ProtagonistItems.protagonist_id == protagonist_id)
                .scalar_subquery()
            )
            query = (
                select(Item)
                .where(Item.location_id == location_id)
                .where(Item.id.not_in(subquery))
            )
            items = (await session.scalars(query)).all()

            return items


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
        ForeignKey("side_effects.id"),
        init=False,
    )
    npc_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("npcs.id"),
        nullable=True,
        init=False,
    )

    side_effect: Mapped["SideEffect"] = relationship(
        default=None,
        lazy=None,
    )

    npc: Mapped["NPC"] = relationship(
        back_populates="quests",
        foreign_keys=[npc_id],
        default=None,
        lazy=None,
    )
    reward: Mapped[Optional["Item"]] = relationship(
        foreign_keys="[Item.reward_for_quest_id]",
        default=None,
        lazy=None,
    )

    required_items: Mapped[list["Item"]] = relationship(
        back_populates="required_for_quest",
        foreign_keys="[Item.required_for_quest_id]",
        default_factory=list,
        lazy=None,
    )

    prerequisite_quests: Mapped[list["Quest"]] = relationship(
        "Quest",
        secondary="prerequisite_quests_table",
        primaryjoin="Quest.id==prerequisite_quests_table.c.parent_quest_id",
        secondaryjoin="Quest.id==prerequisite_quests_table.c.child_quest_id",
        back_populates="prerequisite_quests",
        default_factory=list,
        lazy=None,
    )

    required_npcs: Mapped[list["NPC"]] = relationship(
        secondary="required_npcs_table",
        default_factory=list,
        lazy=None,
    )

    required_enemies: Mapped[list["Enemy"]] = relationship(
        secondary="required_enemies_table",
        default_factory=list,
        lazy=None,
    )

    # def __repr__(self):
    #     quest = f"Квест\nНазвание: {self.name}\nОписание: {self.description}\nДля выполнения требуется:"
    #     quest += "\nВраги: " + ", ".join(
    #         [f"{enemy.name}" for enemy in self.required_enemies]
    #     )
    #     quest += "\nNPCs: " + ", ".join([f"{npc.name}" for npc in self.required_npcs])
    #     quest += "\nПредметы: " + ", ".join(
    #         [f"{item.name}" for item in self.required_items]
    #     )
    #     quest += "\nКвесты: " + ", ".join(
    #         [f"{quest.name}" for quest in self.prerequisite_quests]
    #     )
    #     quest += f"\nНаграда: {self.reward}"

    #     quest += f"\nЭффект: {self.side_effect}"
    #     return quest

    @staticmethod
    async def get_full_quest_info(quest_id: int) -> "Quest":
        async with create_session() as session:
            query = (
                select(Quest)
                .options(
                    selectinload(Quest.required_enemies).selectin_polymorphic(
                        [NPC, Enemy]
                    )
                )
                .options(
                    selectinload(Quest.required_npcs).selectin_polymorphic([NPC, Enemy])
                )
                .options(joinedload(Quest.required_items))
                # .options(joinedload(Quest.prerequisite_quests))
                .options(selectinload(Quest.reward))
                .where(Quest.id == quest_id)
            )

            quest = await session.scalar(query)
            return quest

    async def is_available(quest_id: int):
        """Проверить можно ли взять квест"""
        pass


prerequisite_quests = Table(
    "prerequisite_quests_table",
    Base.metadata,
    Column("parent_quest_id", ForeignKey("quests.id"), primary_key=True),
    Column("child_quest_id", ForeignKey("quests.id"), primary_key=True),
)
required_npcs_table = Table(
    "required_npcs_table",
    Base.metadata,
    Column("quest_id", ForeignKey("quests.id"), primary_key=True),
    Column("npc_id", ForeignKey("npcs.id"), primary_key=True),
)
required_enemies_table = Table(
    "required_enemies_table",
    Base.metadata,
    Column("quest_id", ForeignKey("quests.id"), primary_key=True),
    Column("enemy_id", ForeignKey("enemies.id"), primary_key=True),
)


class Item(Entity, kw_only=True):
    """Предмет, который может использовать персонаж"""

    __tablename__ = "items"

    side_effect_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("side_effects.id"),
        nullable=True,
        init=False,
    )
    enemy_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("enemies.id"),
        nullable=True,
        init=False,
    )
    reward_for_quest_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("quests.id"),
        nullable=True,
        init=False,
    )
    location_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("locations.id"),
        nullable=True,
        init=False,
    )
    required_for_quest_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("quests.id"),
        nullable=True,
        init=False,
    )

    side_effect: Mapped["SideEffect"] = relationship(
        default=None,
        lazy=None,
    )
    enemy: Mapped["Enemy"] = relationship(
        back_populates="items",
        default=None,
        lazy=None,
    )
    location: Mapped["Location"] = relationship(
        back_populates="items",
        default=None,
        lazy=None,
    )

    required_for_quest: Mapped["Quest"] = relationship(
        back_populates="required_items",
        foreign_keys=required_for_quest_id,
        default=None,
        lazy=None,
    )

    __table_args__ = (
        CheckConstraint(
            "(reward_for_quest_id IS NOT NULL) + (enemy_id IS NOT NULL) + (location_id IS NOT NULL) = 1",
            name="one_not_null_check",
        ),
    )

    # def apply_side_effect(self, *, character: Union["Protagonist", "Enemy"]) -> None:
    #     if self.side_effect:
    #         self.side_effect.apply(character)


# Изменяемые таблицы


class Protagonist(HpStrengthMixin, BaseCharacter, kw_only=True):
    """Протагонист"""

    __tablename__ = "protagonists"

    id: Mapped[int] = mapped_column(ForeignKey("characters.id"), primary_key=True)
    location_id: Mapped[int] = mapped_column(ForeignKey("locations.id"), init=False)
    location: Mapped["Location"] = relationship(default=None)

    quests: Mapped[list["ProtagonistQuest"]] = relationship(
        default_factory=list,
        lazy="selectin",
    )
    items: Mapped[list["ProtagonistItems"]] = relationship(
        default_factory=list,
        lazy="selectin",
    )
    met_npcs: Mapped[list["NPC"]] = relationship(
        secondary="met_npcs",
        default_factory=list,
        lazy="selectin",
    )
    defeated_enemies: Mapped[list["Enemy"]] = relationship(
        secondary="defeated_enemies",
        default_factory=list,
        lazy="selectin",
    )
    apllied_side_effect: Mapped[list["SideEffect"]] = relationship(
        secondary="apllied_side_effect",
        default_factory=list,
        lazy="selectin",
    )

    __mapper_args__ = {
        "polymorphic_identity": "protagonist",
    }

    # async def whereami(self) -> Location:
    #     """Получить получить строку описания локации, на которой находиться протагонист, с находящимися там персонажами, предметами"""
    #     location = await Location.get_location_by_id(self.location_id, self)
    #     return location

    # async def go(self, location_id: int) -> None:
    #     async with create_session() as session:
    #         self.location.side_effect.cancel(self)
    #         self.location_id = location_id
    #         session.refresh()

    # async def take_quest():
    #     pass

    # async def take_item(self, *, item_id: int) -> None:

    #     with self.Session() as session:
    #         # self.protagonist.items.append(ProtagonistItems(item_id=item_id, used=False))
    #         pass

    # async def use_item(
    #     self, *, item_id: int, character: Union["Protagonist", "Enemy"]
    # ) -> None:

    #     with self.Session() as session:
    #         for item in self.protagonist.items:
    #             if item.item_id == item_id and item.used == False:
    #                 item.item.apply_effects(character=character)
    #                 item.used = True


met_npcs = Table(
    "met_npcs",
    Base.metadata,
    Column("protagonist_id", ForeignKey("protagonists.id"), primary_key=True),
    Column("npc_id", ForeignKey("npcs.id"), primary_key=True),
)

defeated_enemies = Table(
    "defeated_enemies",
    Base.metadata,
    Column("protagonist_id", ForeignKey("protagonists.id"), primary_key=True),
    Column("enemy_id", ForeignKey("enemies.id"), primary_key=True),
)

apllied_side_effect = Table(
    "apllied_side_effect",
    Base.metadata,
    Column("protagonist_id", ForeignKey("protagonists.id"), primary_key=True),
    Column("side_effect_id", ForeignKey("side_effects.id"), primary_key=True),
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
    used: Mapped[bool] = mapped_column()

    item: Mapped["Item"] = relationship()
