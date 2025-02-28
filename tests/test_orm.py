import pytest
from typing import Any, Generator
from sqlalchemy import create_engine, Engine, select
from sqlalchemy.orm import Session
from get_to_the_clinic_game.orm import (
    Base,
    SideEffect,
    Location,
    NPC,
    Enemy,
    Protagonist,
    Phrase,
    Item,
    Quest,
)


@pytest.fixture
def engine() -> Generator[Any, Any, Engine]:
    engine = create_engine("sqlite://")
    yield engine
    engine.dispose()


@pytest.fixture
def create_tables(engine: Engine) -> None:
    Base.metadata.create_all(engine)


@pytest.fixture
def session(engine: Engine) -> Generator[Any, Any, Session]:
    with Session(engine) as session:
        yield session


@pytest.fixture
def side_effects() -> list[SideEffect]:
    side_effects = [
        SideEffect(
            name="Опыт за главный квест",
            description="За выполение главного квеста +100 к опыту",
            xp_change=100,
        ),
        SideEffect(
            name="Атмосфера в регистраутре",
            description="Атмосфера отчаяния и безнадёги в регистраутре",
            hp_change=-1,
            strength_change=-1,
        ),
        SideEffect(
            name="Эффект сигарет здоровья",
            description="Это великие сигареты здоровья! Курите каждый день по пачке в день и будуте здоровыми :р",
            hp_change=5,
        ),
        SideEffect(
            name="Эффект пончика диабета",
            description="+ 1 к силе",
            strength_change=1,
        ),
    ]

    return side_effects


@pytest.fixture
def locations(side_effects: list[SideEffect]) -> list[Location]:
    locations = [
        Location(
            name="Регистратура",
            description="Ваше первое испытание",
            side_effect=side_effects[1],
        ),
        Location(
            name="Кабинет терапевта",
            description="Это начало начал",
        ),
    ]
    return locations


@pytest.fixture
def npcs(locations: list[Location]) -> list[NPC]:
    npcs = [
        NPC(
            name="Медсестра Иришка Чики-Пики",
            description="Злая тетка, которая работает в регистратуре",
            start_phrase="Что у вас?",
            end_phrase="Следующий!",
            location=locations[0],
        ),
        NPC(
            name="Терапевт Федор",
            description="Это терапевт, он скажет, каких врачей нужно пройти для медосмотра",
            start_phrase="Здраствуйте, проходите. Вы на медосмотр?",
            end_phrase="Вот ваше список врачей которых нужно посетить!",
            xp=100,
            location=locations[0],
        ),
    ]
    return npcs


@pytest.fixture
def enemies(locations: list[Location]) -> list[Location]:

    enemies = [
        Enemy(
            name="Какая-то бабка",
            description="Это ваш первый противник. Стоит в очереди и не дает вам пройти",
            start_phrase="Ты что сквозь очередь лезешь?",
            end_phrase="Ну и молодежь пошла!",
            location=locations[0],
            phrases=[Phrase(phrase="Дебил!"), Phrase(phrase="Дурак!")],
        ),
        Enemy(
            name="Типичная яжмамка",
            description="Пришла со своим мелким дебилом и орет на всю больницу",
            start_phrase="Ну я же мать",
            end_phrase="Ну я же мать!",
            location=locations[1],
            phrases=[Phrase(phrase="Дебил!"), Phrase(phrase="Дурак!")],
        ),
    ]

    return enemies


@pytest.fixture
def items(
    enemies: list[Enemy], locations: list[Location], side_effects: list[SideEffect]
) -> list[Item]:

    items = [
        Item(name="Бутреброд", description="Это же бутерброд!", enemy=enemies[0]),
        Item(
            name="Жвачка",
            description="Чтобы из-за рта не пахло сигами.",
            location=locations[0],
        ),
        Item(
            name="Пончик диабета",
            description="Пончик диабета! сахар +100, сила +1",
            location=locations[1],
            side_effect=side_effects[3],
        ),
        Item(
            name="Сигареты",
            description="Это великие сигареты здоровья! Курите каждый день по пачке в день и будуте здоровыми :р Всем советую!",
            location=locations[1],
        ),
    ]

    return items


@pytest.fixture
def quests(npcs: list[NPC], side_effects: list[SideEffect]) -> list[Quest]:
    quests = [
        Quest(
            name="Иди к терапевту",
            description="Терапевт даст направление с врачами, которые тебе нужно посетить",
            side_effect=side_effects[0],
            npc=npcs[0],
            required_npcs=[npcs[1]],
        )
    ]
    return quests


def test_create_tables(create_tables):
    pass


def test_side_effects(create_tables, side_effects: list[SideEffect], session: Session):
    session.add_all(side_effects)
    session.commit()

    assert side_effects == session.scalars(select(SideEffect)).all()


def test_locations(create_tables, locations: list[Location], session: Session):
    session.add_all(locations)
    session.commit()

    assert locations == session.scalars(select(Location)).all()
    assert locations[1].items == session.scalars(select(Item)).all()


def test_npcs(create_tables, npcs: list[NPC], session: Session):
    session.add_all(npcs)
    session.commit()

    assert npcs == session.scalars(select(NPC)).all()


def test_enemies(create_tables, enemies: list[Enemy], session: Session):
    session.add_all(enemies)
    session.commit()

    assert enemies == session.scalars(select(Enemy)).all()
    assert enemies[0] == session.scalars(select(Enemy).where(Enemy.id == 1)).one()


def test_items(create_tables, items: list[Item], session: Session):
    session.add_all(items)
    session.commit()

    assert items == session.scalars(select(Item)).all()
    assert items[0] == session.scalars(select(Item).where(Item.id == 1)).one()


def test_quests(create_tables, quests: list[Quest], session: Session):
    session.add_all(quests)
    session.commit()

    assert quests == session.scalars(select(Quest)).all()
