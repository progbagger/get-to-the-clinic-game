from typing import List
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from get_to_the_clinic_game.orm import (
    Base,
    Item,
    SideEffect,
    Location,
    NPC,
    Enemy,
    Quest,
)


def create_side_effects() -> List[SideEffect]:
    side_effects = [
        SideEffect(
            name="Опыт за главный квест",
            description="За выполение главного квеста +100 к опыту",
            xp_change=100,
        ),
        SideEffect(
            name="Опыт за побочный квест",
            description="За выполение побочного квеста +50 к опыту",
            xp_change=50,
        ),
        SideEffect(name="+5 к силе", description="+5 к силе", strength_change=5),
        SideEffect(name="+5 к силе", description="+5 к здоровью", hp_change=5),
        SideEffect(
            name="Атмосфера в регистраутре",
            description="Атмосфера отчаяния в регистраутре подействовала на вас",
            hp_change=-1,
            strength_change=-1,
        ),
    ]

    return side_effects


def create_locations() -> List[Location]:
    locations: List[Location] = [
        Location(
            name="Регистратура",
            description="Ваше первое испытание",
            side_effect_id=5,
        ),
        Location(
            name="Кабинет терапевта",
            description="Это начало начал",
            items=[
                Item(
                    name="Пончик",
                    description="Это же пончик!",
                    side_effect_id=3,
                )
            ],
        ),
        Location(name="Кабинет окулиста", description="Тут Зрение проверяют"),
    ]
    locations[0].neighbour_locations.append(locations[1])
    locations[1].neighbour_locations.append(locations[0])
    locations[0].neighbour_locations.append(locations[2])
    locations[2].neighbour_locations.append(locations[0])

    return locations


def create_npc(locations: List[Location]) -> List[Location]:
    npc = [
        NPC(
            name="Медсестра Иришка Чики-Пики",
            description="Злая тетка, которая работает в регистратуре",
            start_phrase="Что у вас?",
            end_phrase="Следующий!",
            location=locations[0],
            xp=50,
        ),
        NPC(
            location=locations[1],
            name="Терапевт Федор",
            description="Это терапевт, он скажет, каких врачей нужно пройти для медосмотра",
            start_phrase="Здраствуйте, проходите. вы на медосмотр?",
            end_phrase="Вот ваше список врачей которых нужно посетить!",
            xp=100,
        ),
        NPC(
            location=locations[2],
            name="Окулист Арсюша",
            description="Проверит зрение",
            start_phrase="Здраствуйте, проходите?",
            end_phrase="У вас зрение -100! Купите очки!",
            xp=150,
        ),
    ]
    print(npc[0])
    return npc


def create_quest() -> List[Item]:
    quests = [
        Quest(
            name="Поговорить с медсестрой в регистратуре",
            description="Вы пришли в поликлинику и вам нужно пройти медосмотр. Поговорите с медсетрой в регистратуре, чтобы узнать, как пройти медосмотр.",
            side_effect_id=1,
            required_npcs=[
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
                            side_effect_id=4,
                        ),
                    ],
                ),
            ],
        ),
        Quest(
            name="Иди к терапевту",
            description="Терапевт даст направление с врачами, которые ты посетил",
            side_effect_id=1,
            npc_id=1,
        ),
    ]

    return quests


if __name__ == "__main__":

    engine = create_engine(
        "sqlite:///db.db",
        echo=True,
    )
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        session.add_all(create_side_effects())
        session.commit()

        session.add_all(locations := create_locations())
        session.commit()

        session.add_all(create_npc(locations))
        session.commit()

        session.add_all(create_quest())
        session.commit()
