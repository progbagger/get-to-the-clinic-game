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
    Phrase,
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


def create_items(*, side_effects: List[SideEffect]) -> List[Item]:
    items = (
        Item(
            name="Бутреброд",
            description="Это же бутерброд!",
            side_effect=side_effects[3],
        ),
        Item(
            name="Пончик",
            description="Это же пончик!",
            side_effect=side_effects[2],
        ),
    )
    return items


def create_quest(
    *,
    side_effects: List[SideEffect],
    items: List[Item],
    npcs: List[NPC],
    enemies: List[Enemy],
) -> List[Quest]:
    quests = [
        Quest(
            name="Поговорить с медсестрой в регистратуре",
            description="Вы пришли в поликлинику и вам нужно пройти медосмотр. Поговорите с медсетрой в регистратуре, чтобы узнать, как пройти медосмотр.",
            side_effect=side_effects[0],
        ),
        Quest(
            name="Иди к терапевту",
            description="Терапевт даст направление с врачами, которые ты посетил",
            side_effect=side_effects[0],
            npc=npcs[0],
        ),
    ]

    return quests


def create_npc() -> List[NPC]:
    npcs = [
        NPC(
            name="Медсестра Иришка Чики-Пики",
            description="Злая тетка, которая работает в регистратуре",
            start_phrase="Что у вас?",
            end_phrase="Следующий!",
            xp=50,
        ),
        NPC(
            name="Терапевт Федор",
            description="Это терапевт, он скажет, каких врачей нужно пройти для медосмотра",
            start_phrase="Здраствуйте, проходите. вы на медосмотр?",
            end_phrase="Вот ваше список врачей которых нужно посетить!",
            xp=100,
        ),
        NPC(
            name="Окулист Арсюша",
            description="Проверит зрение",
            start_phrase="Здраствуйте, проходите?",
            end_phrase="У вас зрение -100! Купите очки!",
            xp=150,
        ),
    ]
    return npcs


def create_enemies(*, items: List[Item]) -> List[Enemy]:
    enemies = [
        Enemy(
            name="Какая-то бабка",
            description="Это ваш первый противник. Стоит в очереди и не дает вам пройти",
            start_phrase="Ты что сквозь очередь лезешь?",
            end_phrase="Ну и молодежь пошла!",
            xp=0,
            hp=10,
            strength=10,
            items=[items[0]],
            phrases=[Phrase(phrase="Дурак!"), Phrase(phrase="Дебил!")],
        ),
    ]
    return enemies


def create_locations(
    *,
    side_effects: List[SideEffect],
    items: List[Item],
    npcs: List[NPC],
    enemies: List[Enemy],
) -> List[Location]:
    locations: List[Location] = [
        Location(
            name="Регистратура",
            description="Ваше первое испытание",
            side_effect=side_effects[4],
            npcs=[npcs[0], enemies[0]],
        ),
        Location(
            name="Кабинет терапевта",
            description="Это начало начал",
            items=[items[1]],
            npcs=[npcs[1]],
        ),
        Location(
            name="Кабинет окулиста",
            description="Тут зрение проверяют",
            npcs=[npcs[2]],
        ),
    ]
    locations[0].neighbour_locations.append(locations[1])
    locations[1].neighbour_locations.append(locations[0])
    locations[0].neighbour_locations.append(locations[2])
    locations[2].neighbour_locations.append(locations[0])

    return locations


if __name__ == "__main__":

    engine = create_engine(
        "sqlite:///db.db",
        echo=True,
    )
    Base.metadata.create_all(engine)

    with Session(engine) as session:

        side_effects = create_side_effects()
        items = create_items(side_effects=side_effects)
        npcs = create_npc()
        enemies = create_enemies(items=items)
        quests = create_quest(
            side_effects=side_effects, items=items, npcs=npcs, enemies=enemies
        )
        locations = create_locations(
            side_effects=side_effects, items=items, npcs=npcs, enemies=enemies
        )
        session.add_all(side_effects)
        session.add_all(items)
        session.add_all(npcs)
        session.add_all(enemies)
        session.add_all(quests)
        session.add_all(locations)
        session.commit()
