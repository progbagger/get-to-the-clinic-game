from typing import List
from sqlalchemy import Engine, create_engine, select
from sqlalchemy.orm import Session, sessionmaker
from get_to_the_clinic_game.orm import Protagonist, Location


class Game:
    def __init__(self, connection_string: str) -> None:
        self.engine: Engine = create_engine(connection_string)
        self.Session = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self.session = self.Session()
        self.protagonist: Protagonist | None = None

    def protagonist_exists(self, id: int) -> bool:
        with Session(self.engine) as session:
            user = session.scalar(select(Protagonist).where(Protagonist.id == id))
            return bool(user)

    def create_game(self, id: int, name: str) -> None:
        with Session(self.engine) as session:
            self.protagonist = Protagonist(
                id=id,
                name=name,
                description="Это ты. Ты пришел в это адовое место под названием поликлиника, чтобы пройти медосмотр для военкомата. Удачи тебе!",
                start_phrase=f"Привет, {name}",
                end_phrase=f"Пока, {name}",
                location=session.scalar(
                    select(Location).where(Location.name == "Регистратура")
                ),
            )

            session.add(self.protagonist)
            session.commit()
            session.refresh(self.protagonist)

    def load_game(self, id: int) -> None:
        with Session(self.engine) as session:
            self.protagonist = session.scalar(
                select(Protagonist).where(Protagonist.id == id)
            )

    def cur_location(self) -> str:

        return self.protagonist.whereami(self.session)

    def get_characters(self):
        return self.protagonist.location.get_characters(self.session)
