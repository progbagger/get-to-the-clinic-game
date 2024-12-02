from typing import List
from sqlalchemy import Engine, create_engine, select
from sqlalchemy.orm import Session
from game.orm import Protagonist


class Game:
    def __init__(self, connection_string: str) -> None:
        self.engine: Engine = create_engine(connection_string)
        self.protagonist: Protagonist | None = None

    def is_protagonist_exists(self, id: int) -> bool:
        with Session(self.engine) as session:
            user = session.scalar(select(Protagonist).where(Protagonist.id == id))
            return bool(user)

    def create_game(self, id: int, name: str) -> None:
        with Session(self.engine) as session:
            self.protagonist = Protagonist(
                id=id,
                name=name,
                description="Это ты. Ты пришел в это адовое место под названием поликлиника, чтобы пройти медосмотр для военкомата. Удачи тебе!",
                start_phrase="Привет, дебил",
                end_phrase="Пока, дебил",
            )

            session.add(self.protagonist)
            session.commit()
            session.refresh(self.protagonist)

    def load_game(self, id: int) -> None:
        with Session(self.engine) as session:
            self.protagonist = session.scalar(
                select(Protagonist).where(Protagonist.id == id)
            )
