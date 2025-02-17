import asyncio
from sqlalchemy import Engine, create_engine, select

from sqlalchemy.ext.asyncio import AsyncSession
from get_to_the_clinic_game.orm.database import create_session
from get_to_the_clinic_game.orm import (
    Protagonist,
    Location,
    NPC,
    Enemy,
    Character,
    Quest,
    Phrase,
    Item,
)


class Game:
    def __init__(self) -> None:
        self.protagonist: Protagonist | None = None

    @staticmethod
    async def protagonist_exists(*, id: int) -> bool:
        async with create_session() as session:
            user = await session.get(Protagonist, id)
        return bool(user)

    async def create_protagonist(self, *, id: int, name: str) -> None:
        async with create_session() as session:
            self.protagonist = Protagonist(
                id=id,
                name=name,
                description="Это ты. Ты пришел в это адовое место под названием поликлиника, чтобы пройти медосмотр для военкомата. Удачи тебе!",
                start_phrase=f"Привет, {name}",
                end_phrase=f"Пока, {name}",
                location=await session.scalar(
                    select(Location).where(Location.name == "Регистратура")
                ),
            )

            session.add(self.protagonist)
            await session.commit()
            await session.refresh(self.protagonist)

    async def load_protagonist(self, *, id: int) -> None:
        async with create_session() as session:
            self.protagonist = await session.get(Protagonist, id)


# class Protagonist:
#     def __init__(self, Session: sessionmaker[Session]) -> None:
#         self.protagonist: ProtagonistORM | None = None
#         self.Session = Session


# def go(self, location_id: int) -> None:
#     with self.Session() as session:
#         # добавить side effects
#         self.location_id = location_id
#         session.refresh()

# def talk_to(self, *, character_id: Character) -> NPC | Enemy:
#     with self.Session() as session:
#         character: NPC | Enemy = session.scalar(
#             select(Character)
#             .filter(Character.id == character_id)
#             .options(
#                 selectin_polymorphic(Character, [NPC, Enemy]),
#             )
#         )
#         if character == "npc":
#             protagonist_quests = {
#                 quest.quest_id for quest in self.protagonist.quests
#             }
#             filter_quests = [
#                 quest
#                 for quest in character.quests
#                 if quest.id not in protagonist_quests
#             ]
#             character.quests = filter_quests

#     return character

# def take_item(self, *, item_id: int) -> None:
#     with self.Session() as session:
#         # self.protagonist.items.append(ProtagonistItems(item_id=item_id, used=False))
#         pass

# def use_item(self, *, item_id: int, character: Enemy | "ProtagonistORM") -> None:

#     with self.Session() as session:
#         for item in self.protagonist.items:
#             if item.item_id == item_id and item.used == False:
#                 item.item.apply_effects(character=character)
#                 item.used = True
