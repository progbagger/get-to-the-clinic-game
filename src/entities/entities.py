from enum import Enum, auto
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
    declared_attr,
)
from sqlalchemy import String, Integer, ARRAY, ForeignKey
from typing import Optional


BASE_XP: int = 0
BASE_HP: int = 10
BASE_STRENGTH: int = 1

BASE_STRENGTH_CHANGE = 1


class GameException(Exception):
    pass


class UsedItemException(GameException):
    pass


class Base(DeclarativeBase):
    pass


class BaseEntity(Base):
    __abstract__ = True

    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str]
    description: Mapped[str]

    def __init__(self, name: str, description: str) -> None:
        self.name = name
        self.description = description


class Entity(BaseEntity):
    __abstract__ = True

    xp: Mapped[int]
    start_phrase: Mapped[str]
    end_phrase: Mapped[str]
    middle_phrases: Mapped[list[str]] = mapped_column(ARRAY(String))
    item_ids: Mapped[int] = mapped_column(ForeignKey("item.id"))

    @declared_attr
    def items(cls) -> Mapped[list["Item"]]:
        return relationship("Item", foreign_keys=[cls.item_ids])

    def __init__(
        self,
        name: str,
        description: str,
        start_phrase: str,
        end_phrase: str,
        xp: int = BASE_XP,
        items: Optional[list["Item"]] = None,
        middle_phrases: Optional[list[str]] = None,
    ) -> None:
        super().__init__(name=name, description=description)

        self.start_phrase = start_phrase
        self.end_phrase = end_phrase
        self.xp = xp
        self.middle_phrases = middle_phrases if not None else []
        self.items = items if not None else []
        self.item_ids = [item.id for item in self.items]


class SideEffect(BaseEntity):
    __tablename__ = "side_effect"

    hp_change: Mapped[int]
    xp_change: Mapped[int]
    strength_change: Mapped[int]
    item_ids: Mapped[list[int]] = mapped_column(ForeignKey("item.id"))

    @declared_attr
    def items(cls) -> Mapped[list["Item"]]:
        return relationship("Item", foreign_keys=[cls.item_ids])

    def __init__(
        self,
        name: str,
        description: str,
        hp_change: int = 0,
        xp_change: int = 0,
        strength_change: int = 0,
        items: Optional[list["Item"]] = None,
    ) -> None:
        super().__init__(name=name, description=description)

        self.hp_change = hp_change
        self.xp_change = xp_change
        self.strength_change = strength_change
        self.items = items if not None else []
        self.item_ids = [item.id for item in self.items]


class Item(BaseEntity):
    __tablename__ = "item"

    value: Mapped[int]
    side_effect_id: Mapped[Optional[int]] = mapped_column(ForeignKey("side_effect.id"))
    side_effect: Mapped[Optional[SideEffect]] = relationship(
        foreign_keys=[side_effect_id]
    )
    is_used: Mapped[bool]

    def __init__(
        self,
        name: str,
        description: str,
        value: int = 0,
        side_effect: Optional[SideEffect] = None,
        is_used: bool = False,
    ) -> None:
        super().__init__(name=name, description=description)

        self.value = value
        self.side_effect = side_effect
        self.side_effect_id = self.side_effect.id if self.side_effect else None
        self.is_used = is_used

    def use(self, enemy: "Enemy") -> None:
        if self.is_used:
            raise UsedItemException(f'Предмет "{self.name}" уже использован')

        enemy.hp += self.side_effect.hp_change
        enemy.strength += self.side_effect.strength_change
        enemy.xp += self.side_effect.xp_change


class Enemy(Entity):
    __tablename__ = "enemy"
    __allow_unmapped__ = True

    hp: Mapped[int]
    strength: Mapped[int]
    item_ids: Mapped[list[int]] = mapped_column(ForeignKey("item.id"))
    items: Mapped[list[Item]] = relationship(foreign_keys=[item_ids])

    level: int

    def __init__(
        self,
        name: str,
        description: str,
        start_phrase: str,
        end_phrase: str,
        xp: int = BASE_XP,
        hp: int = BASE_HP,
        strength: int = BASE_STRENGTH,
        items: Optional[Item] = None,
        middle_phrases: Optional[str] = None,
    ) -> None:
        super().__init__(
            name=name,
            description=description,
            start_phrase=start_phrase,
            end_phrase=end_phrase,
            xp=xp,
            items=items,
            middle_phrases=middle_phrases,
        )

        self.hp = hp
        self.strength = strength

        self.level = self.current_level

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
        """Повышает уровень и возвращает количество полученных уровней"""

        if self.level == self.current_level:
            return 0

        result = self.current_level - self.level
        self.strength += result * BASE_STRENGTH_CHANGE

        return result

    def attack(self, enemy: "Enemy", amount: int = 1) -> None:
        enemy.take_hit(amount)


class NPC(Entity):
    __tablename__ = "npc"

    quest_ids: Mapped[list[int]] = mapped_column(ForeignKey("quest.id"))

    @declared_attr
    def quests(cls) -> Mapped[list["Quest"]]:
        return relationship("Quest", cls.quest_ids)

    def __init__(
        self,
        name: str,
        description: str,
        start_phrase: str,
        end_phrase: str,
        xp: int = BASE_XP,
        items: Optional[list["Item"]] = None,
        middle_phrases: Optional[list[str]] = None,
        quests: Optional[list["Quest"]] = None,
    ) -> None:
        super().__init__(
            name=name,
            description=description,
            start_phrase=start_phrase,
            end_phrase=end_phrase,
            xp=xp,
            items=items,
            middle_phrases=middle_phrases,
        )

        self.quests = quests if not None else []
        self.quest_ids = [quest.id for quest in self.quests]

    def take_quests(self) -> list["Quest"]:
        result = self.quests
        self.quests.clear()
        self.quest_ids.clear()

        return result


class Protagonist(Entity):
    __tablename__ = "protagonist"

    quest_ids: Mapped[list[int]] = mapped_column(ForeignKey("quest.id"))

    @declared_attr
    def quests(cls) -> Mapped[list["Quest"]]:
        return relationship("Quest")

    def __init__(
        self,
        name: str,
        description: str,
        start_phrase: str,
        end_phrase: str,
        xp: int = BASE_XP,
        items: Optional[list["Item"]] = None,
        middle_phrases: Optional[list[str]] = None,
        quests: Optional[list["Quest"]] = None,
    ) -> None:
        super().__init__(
            name=name,
            description=description,
            start_phrase=start_phrase,
            end_phrase=end_phrase,
            xp=xp,
            items=items,
            middle_phrases=middle_phrases,
        )

        self.quests = quests if not None else []
        self.quest_ids = [quest.id for quest in self.quests]

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

    required_enemy_ids: Mapped[list[int]] = mapped_column(ForeignKey("enemy.id"))
    required_enemies: Mapped[list[Enemy]] = relationship(
        foreign_keys=[required_enemy_ids]
    )

    required_npc_ids: Mapped[list[int]] = mapped_column(ForeignKey("npc.id"))
    required_npcs: Mapped[list[NPC]] = relationship(foreign_keys=[required_npc_ids])

    required_item_ids: Mapped[list[int]] = mapped_column(ForeignKey("item.id"))
    required_items: Mapped[list[Item]] = relationship(foreign_keys=[required_item_ids])

    reward_id: Mapped[int] = mapped_column(ForeignKey("side_effect.id"))
    reward: Mapped[SideEffect] = relationship(foreign_keys=[reward_id])

    status: Mapped[QuestStatus]

    def __init__(
        self,
        name: str,
        description: str,
        reward: SideEffect,
        required_enemies: Optional[list[Enemy]] = None,
        required_npcs: Optional[list[NPC]] = None,
        required_items: Optional[list[Item]] = None,
        status: QuestStatus = QuestStatus.NOT_STARTED,
    ) -> None:
        super().__init__(name=name, description=description)

        self.reward = reward
        self.reward_id = reward.id

        self.required_enemies = required_enemies if not None else []
        self.required_enemy_ids = [enemy.id for enemy in self.required_enemies]

        self.required_npcs = required_npcs if not None else []
        self.required_npc_ids = [npc.id for npc in self.required_npcs]

        self.required_items = required_items if not None else []
        self.required_item_ids = [item.id for item in self.required_items]

        self.status = status


class Location(BaseEntity):
    __tablename__ = "location"

    location_ids: Mapped[list[int]] = mapped_column(ForeignKey("location.id"))

    @declared_attr
    def locations(cls) -> Mapped[list["Location"]]:
        return relationship("Location")

    npc_ids: Mapped[list[int]] = mapped_column(ForeignKey("npc.id"))
    npcs: Mapped[list[NPC]] = relationship()

    enemy_ids: Mapped[list[int]] = mapped_column(ForeignKey("enemy.id"))
    enemies: Mapped[list[Enemy]] = relationship()

    side_effect_id: Mapped[Optional[int]] = mapped_column(ForeignKey("side_effect.id"))
    side_effect: Mapped[Optional[SideEffect]] = relationship()

    def __init__(
        self,
        name: str,
        description: str,
        locations: Optional[list["Location"]] = None,
        npcs: Optional[list[NPC]] = None,
        enemies: Optional[list[Enemy]] = None,
        side_effect: Optional[SideEffect] = None,
    ) -> None:
        super().__init__(name=name, description=description)

        self.locations = locations if not None else []
        self.location_ids = [location.id for location in self.locations]

        self.npcs = npcs if not None else []
        self.npc_ids = [npc.id for npc in self.npcs]

        self.enemies = enemies if not None else []
        self.enemy_ids = [enemy.id for enemy in self.enemies]

        self.side_effect = side_effect
        self.side_effect_id = self.side_effect.id if self.side_effect else None


SideEffect(name="buff", description="sus")
