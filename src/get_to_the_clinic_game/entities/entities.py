import asyncio
from sqlalchemy import select
from get_to_the_clinic_game.orm.database import db_manager
from get_to_the_clinic_game.orm import (
    Protagonist,
    Location,
)


class Game:

    @staticmethod
    async def protagonist_exists(id: int) -> bool:
        async with db_manager.get_session() as session:
            user = await session.get(Protagonist, id)

            return bool(user)

    @staticmethod
    async def create_protagonist(id: int, name: str) -> None:
        async with db_manager.get_session() as session:
            protagonist = Protagonist(
                id=id,
                name=name,
                description="Это ты. Ты пришел в это адовое место под названием поликлиника, чтобы пройти медосмотр для военкомата. Удачи тебе!",
                start_phrase=f"Привет, {name}",
                end_phrase=f"Пока, {name}",
                location=await session.scalar(
                    select(Location).where(Location.name == "Регистратура")
                ),
            )

            session.add(protagonist)
            await session.commit()
