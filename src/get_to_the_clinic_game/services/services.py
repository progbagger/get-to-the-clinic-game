import asyncio
from typing import Union
from sqlalchemy import select
from sqlalchemy.orm import selectin_polymorphic, joinedload, selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from get_to_the_clinic_game.orm import (
    Protagonist,
    ProtagonistItems,
    ProtagonistQuest,
    Location,
    connected_locations,
    Character,
    Enemy,
    NPC,
    Item,
    Quest,
    Status,
    defeated_enemies,
)

session: AsyncSession | None = None


def _set_session(s: AsyncSession) -> None:
    global session
    session = s


def _remove_session() -> None:
    global session
    session = None


class LocationService:

    @staticmethod
    async def get_location_details(location_id: int, protagonist_id: int) -> "Location":
        """Получение полной информации о локации: эффект локации, персонажи, предметы, соседние локации"""

        defeated_enemies_subquery = (
            select(defeated_enemies.c.enemy_id)
            .where(defeated_enemies.c.protagonist_id == protagonist_id)
            .scalar_subquery()
        )

        collected_items_subquery = (
            select(ProtagonistItems.item_id)
            .where(ProtagonistItems.protagonist_id == protagonist_id)
            .scalar_subquery()
        )

        query = (
            select(Location)
            .options(selectinload(Location.side_effect))
            .options(selectinload(Location.characters))
            .options(joinedload(Location.items))
            .options(joinedload(Location.neighbour_locations))
            .where(Character.id.not_in(defeated_enemies_subquery))
            .where(Item.id.not_in(collected_items_subquery))
            .where(Location.id == location_id)
        )

        location: Location = await session.scalar(query)

        return location

    @staticmethod
    async def get_neighbour_locations(location_id: int) -> list["Location"]:
        """Получение все соседнии локации"""

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
    async def get_characters_by_location(
        location_id: int, protagonist_id: int
    ) -> list["Character"]:
        """Получить всех персонажей на локации, кроме побежденных"""

        defeated_enemies_subquery = (
            select(defeated_enemies.c.enemy_id)
            .where(defeated_enemies.c.protagonist_id == protagonist_id)
            .scalar_subquery()
        )

        query = (
            select(Character)
            .where(Character.location_id == location_id)
            .where(Character.id.not_in(defeated_enemies_subquery))
        )
        characters = (await session.scalars(query)).all()

        return characters

    @staticmethod
    async def get_items_by_location(
        location_id: int, protagonist_id: int
    ) -> list["Item"]:
        """Получить все предметы на локации, кроме собранных"""

        collected_items_subquery = (
            select(ProtagonistItems.item_id)
            .where(ProtagonistItems.protagonist_id == protagonist_id)
            .scalar_subquery()
        )

        query = (
            select(Item)
            .where(Item.location_id == location_id)
            .where(Item.id.not_in(collected_items_subquery))
        )
        items = (await session.scalars(query)).all()

        return items


class CharacterService:
    @staticmethod
    async def get_character_details(character_id: int) -> Union["Enemy", "NPC"]:
        """Получение полной информации о персонаже"""

        query = (
            select(Character)
            .options(
                selectin_polymorphic(Character, [NPC, Enemy]),
                selectinload(NPC.quests),
                selectinload(Enemy.items),
            )
            .where(Character.id == character_id)
        )
        character: Enemy = await session.scalar(query)
        return character


class QuestService:
    @staticmethod
    async def get_quest_details(quest_id: int) -> "Quest":
        """Получить полную информацию о квесте:"""

        query = (
            select(Quest)
            .options(
                selectinload(Quest.required_enemies).selectin_polymorphic([NPC, Enemy])
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


class ItemService:
    @staticmethod
    async def get_item_details(item_id: int) -> "Item":
        """Получить полную информацию о предмете:"""

        query = (
            select(Item)
            .options(selectinload(Item.side_effect))
            .options(joinedload(Item.required_for_quest))
            .where(Item.id == item_id)
        )

        item = await session.scalar(query)
        return item

    @staticmethod
    async def use_item():
        pass


class ProtagonistService:
    @staticmethod
    async def protagonist_exists(id: int) -> bool:

        user = await session.get(Protagonist, id)

        return bool(user)

    @staticmethod
    async def create_protagonist(id: int, name: str) -> None:

        protagonist = Protagonist(
            id=id,
            name=name,
            description="Ты пришел в этот ад под названием поликлиника, чтобы пройти медосмотр для военкомата. Удачи тебе!",
            start_phrase=f"Привет, {name}",
            end_phrase=f"Пока, {name}",
            location=await session.scalar(
                select(Location).where(Location.name == "Регистратура")
            ),
        )

        session.add(protagonist)
        await session.commit()

    @staticmethod
    async def get_protagonist_details(protagonist_id: int) -> "Protagonist":
        """Получить текущие характеристики протагониста и его локацию по его id"""
        query = (
            select(Protagonist)
            .options(selectinload(Protagonist.location))
            .where(Protagonist.id == protagonist_id)
        )
        protoganist = await session.scalar(query)
        return protoganist

    @staticmethod
    async def get_protagonist_items(
        protagonist_id: int, used: bool = False
    ) -> list[Item]:

        query = (
            select(Item)
            .options(joinedload(ProtagonistItems))
            .where(ProtagonistItems.protagonist_id == protagonist_id)
            .where(ProtagonistItems.used is used)
        )
        quests = await session.scalar(query)
        return quests

    @staticmethod
    async def get_protagonist_quests(
        protagonist_id: int, status: Status = Status.InProgress
    ) -> list[Quest]:

        query = (
            select(Quest)
            .options(joinedload(ProtagonistQuest))
            .where(ProtagonistQuest.protagonist_id == protagonist_id)
            .where(ProtagonistQuest.status == status)
        )
        quests = await session.scalar(query)
        return quests

    @staticmethod
    async def go(protagonist_id: int, location_id: int) -> None:

        query = (
            select(Protagonist)
            .outerjoin(Protagonist.location)
            .outerjoin(Location.side_effect)
            .where(Protagonist.id == protagonist_id)
        )

        protagonist = await session.scalar(query)
        print(protagonist)

        if protagonist.location.side_effect is not None:
            protagonist.location.side_effect.cancel(protagonist)

        protagonist.location_id = location_id

        await session.commit()
        await session.refresh(protagonist)
        print(protagonist.location.side_effect)

        if protagonist.location.side_effect is not None:
            protagonist.location.side_effect.apply(protagonist)
        await session.commit()

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
