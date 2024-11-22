from typing import List
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from orm import Base, Item, SideEffect, Location, NPC, Enemy, Quest


def create_side_effects() -> List[SideEffect]:
    side_effects = [
        SideEffect(name="+5 к силе", description="+5 к силе", strength_change=5),
        SideEffect(name="+5 к здоровью", description="+5 к здоровью", hp_change=5),
        SideEffect(name="+50 к опыту", description="+50 к опыту", xp_change=50),
        SideEffect(
            name="Очередь к регистратуре",
            description="Нахождение в очереди к регистратуре сказалась на вас не лучшим образом",
            hp_change=-1,
            strength_change=-1,
        ),
    ]

    return side_effects


def create_locations() -> List[Location]:
    locations = [
        Location(
            id=1,
            name="Регистратура",
            description="Ваше первое испытание",
            side_effect_id=3,
        ),
        Location(
            id=2,
            name="Кабинет терапевта",
            description="Это начало начал",
            items=[
                Item(
                    name="Пончик",
                    description="Это же пончик!",
                    side_effect_id=1,
                )
            ],
        ),
        Location(id=3, name="Кабинет окулиста", description="Тут Зрение проверяют"),
    ]
    return locations


def create_npc() -> List[Location]:
    npc = [
        NPC(
            id=1,
            name="Медсестра Иришка Чики-Пики",
            description="Злая тетка, которая работает в регистратуре",
            start_phrase="Что у вас?",
            end_phrase="Следующий!",
            location_id=1,
            xp=50,
        ),
        NPC(
            id=2,
            name="Терапевт Федор",
            description="Это терапевт, он скажет, каких врачей нужно пройти для медосмотра",
            start_phrase="Здраствуйте, проходите. вы на медосмотр?",
            end_phrase="Вот ваше список врачей которых нужно посетить!",
            location_id=2,
            xp=100,
        ),
        NPC(
            id=3,
            name="Окулист Арсюша",
            description="Проверит зрение",
            start_phrase="Здраствуйте, проходите?",
            end_phrase="У вас зрение -100! Купите очки!",
            location_id=3,
            xp=150,
        ),
    ]
    return npc


# def create_items() -> List[Item]:
#     items = [
#         Item(name="Бутреброд", description="Это же бутерброд!", side_effect_id=2),
#     ]

#     return items


def create_quest() -> List[Item]:
    quests = [
        Quest(
            id=1,
            name="Поговорить с медсестрой в регистратуре",
            description="Вы пришли в поликлинику и вам нужно пройти медосмотр. Поговорите с медсетрой в регистратуре, чтобы узнать, как пройти медосмотр.",
            side_effect_id=3,
            required_npc=[
                Enemy(
                    name="Какая-то бабка",
                    description="Это ваш первый противник. Стоит в очереди и не дает вам пройти",
                    start_phrase="Ты что сквозь очередь лезешь?",
                    end_phrase="Ну и молодежь пошла!",
                    location_id=1,
                    xp=0,
                    hp=10,
                    strength=10,
                    items=[
                        Item(
                            name="Бутреброд",
                            description="Это же бутерброд!",
                            side_effect_id=2,
                        ),
                    ],
                ),
            ],
        ),
        Quest(
            id=2,
            name="Иди к терапевту",
            description="Терапевт даст направление с врачами, которые ты посетил",
            side_effect_id=3,
            npc_id=1,
        ),
    ]

    return quests


if __name__ == "__main__":

    engine = create_engine(
        "sqlite:///database.db",
        echo=True,
    )
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        session.add_all(create_side_effects())
        session.commit()

        session.add_all(create_locations())
        session.commit()

        session.add_all(create_npc())
        session.commit()

        session.add_all(create_quest())
        session.commit()
