from typing import List
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from orm import Base, Item, SideEffect, Location, NPC, Enemy, Quest


def create_side_effects() -> List[SideEffect]:
    side_effects = [
        SideEffect(name="+5 к силе", description="+5 к силе", strength_change=5),
        SideEffect(name="+5 к здоровью", description="+5 к здоровью", hp_change=5),
        SideEffect(
            name="Очередь к регистратуре",
            description="Нахождение в очереди к регистратуре сказалась на вас не лучшим образом",
            hp_change=-1,
            strength_change=-1,
        ),
    ]

    return side_effects


def create_items() -> List[Item]:
    items = [
        Item(name="Пончик", description="Это же пончик!", side_effect_id=1),
        Item(name="Бутреброд", description="Это же бутерброд!", side_effect_id=2),
    ]

    return items


def create_quest() -> List[Item]:
    quests = [
        Quest(
            name="Иди к терапевту",
            description="Терапевт даст направление с врачами, которые ты посетил",
        ),
        Quest(
            name="Победи бабку в очереди",
            description="Бабка в очреди к региструтуре мешает вам. Заставьте ее уйти!",
            side_effect_id=1,
            reqired_enemies=[
                Enemy(
                    name="Какая-то бабка",
                    dedcription="Стоит в очереди и не дает вам пройти",
                    start_phrase="Что тебе?",
                    end_phrase="Ну и моложежь пошла!",
                )
            ],
        ),
    ]

    return quests


def create_locations() -> List[Location]:
    locations = [
        Location(
            name="Регистратура",
            description="Ваше первое испытание",
            side_effect_id=3,
            npc=[
                NPC(
                    name="Медсестра Иришка Чики-Пики",
                    description="Злая тетка, которая работает в регистратуре",
                    start_phrase="Что у вас?",
                    end_phrase="Следующий!",
                ),
            ],
        ),
        # Location(name="Кабинет окулиста", description="Тут зрение проверяют"),
    ]
    return locations


if __name__ == "__main__":

    engine = create_engine(
        "sqlite:///database",
        echo=True,
    )
    Base.metadata.create_all(engine)
with Session(engine) as session:
    session.add_all(create_side_effects())
    session.commit()

    session.add_all(create_items())
    session.commit()

    session.add_all(create_locations())
    session.commit()

    # chel = session.scalars(select(NPC).filter_by(location_id=1)).one()
