from abc import ABC, abstractmethod
from typing import List
from orm import Status


class Entity(ABC):

    @abstractmethod
    def __init__(self, *, name: str, description: str) -> None:
        self.name = name
        self.description = name


class Character(Entity):

    @abstractmethod
    def __init__(
        self,
        *,
        name: str,
        description: str,
        xp: int,
        items: List["Item"] | None = None,
        start_phrase: str,
        end_phrase: str,
        middle_phrases: List[str],
    ) -> None:
        super().__init__(name=name, description=description)
        self.xp = xp
        self.items = items
        self.start_phrase = start_phrase
        self.end_phrase = end_phrase
        self.middle_phrases = middle_phrases


class NPC(Character):

    def __init__(
        self,
        *,
        name: str,
        description: str,
        xp: int,
        items: List["Item"] | None = None,
        start_phrase: str,
        end_phrase: str,
        middle_phrases: List[str],
        quests: List["Quest"],
    ):
        super().__init__(
            name=name,
            description=description,
            xp=xp,
            items=items,
            start_phrase=start_phrase,
            end_phrase=end_phrase,
            middle_phrases=middle_phrases,
        )
        self.quests = quests


class Enemy(Character):

    def __init__(
        self,
        *,
        name: str,
        description: str,
        xp: int,
        items: List["Item"],
        start_phrase: str,
        end_phrase: str,
        middle_phrases: List[str],
        hp: int,
        strength: int,
    ) -> None:
        super().__init__(
            name=name,
            description=description,
            xp=xp,
            items=items,
            start_phrase=start_phrase,
            end_phrase=end_phrase,
            middle_phrases=middle_phrases,
        )
        self.hp = hp
        self.strength = strength

    def heal(anount: int = 1) -> None:
        pass

    def take_hit(anount: int = 1) -> None:
        pass

    def attack(enemy: "Enemy", anount: int = 1) -> None:
        pass


class Protagonist(Enemy):

    def __init__(
        self,
        *,
        name: str,
        description: str,
        xp: int,
        items: List["Item"],
        start_phrase: str,
        end_phrase: str,
        middle_phrases: List[str],
        hp: int,
        strength: int,
    ):
        super().__init__(
            name=name,
            description=description,
            xp=xp,
            items=items,
            start_phrase=start_phrase,
            end_phrase=end_phrase,
            middle_phrases=middle_phrases,
            hp=hp,
            strength=strength,
        )


class SideEffect(Entity):

    def __init__(
        self,
        *,
        name: str,
        description: str,
        xp_change: int = 0,
        hp_change: int = 0,
        strength_change: int = 0,
    ):
        super().__init__(name=name, description=description)
        self.xp_change = xp_change
        self.hp_change = hp_change
        self.strength_change = strength_change

    def apply(character: Enemy) -> None:
        pass


class Item(Entity):

    def __init__(
        self, *, name: str, description: str, side_effect: SideEffect | None = None
    ):
        super().__init__(name=name, description=description)
        self.side_effect = side_effect

    def use(character: Enemy) -> None:
        pass


class Quest(Entity):

    def __init__(
        self,
        *,
        name: str,
        description: str,
        required_enemies: List[Enemy] = None,
        required_npcs: List[NPC] = None,
        required_items: List[Item] = None,
        side_effect: SideEffect,
        reward: Item = None,
        status: Status = Status.NotStarted,
    ):
        super().__init__(name=name, description=description)
        self.required_enemies = required_enemies
        self.required_npcs = required_npcs
        self.required_items = required_items
        self.side_effect = side_effect
        self.reward = reward
        self.status = status


class Location(Entity):

    def __init__(
        self,
        *,
        name: str,
        description: str,
        side_effect: SideEffect | None = None,
        neighbour_locations: List["Location"] | None,
        npcs: List[NPC] | None = None,
        enemies: List[Enemy] | None = None,
        items: List["Item"] | None = None,
    ) -> None:
        super().__init__(name=name, description=description)
        self.side_effect = side_effect
        self.neighbour_locations = neighbour_locations
        self.npcs = npcs
        self.enemies = enemies
        self.items = items


class Game:
    pass
