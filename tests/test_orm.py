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
def add_data(create_tables, session: Session) -> None:
    quest_side_effect = SideEffect(
        name="Опыт за главный квест",
        description="За выполение главного квеста +100 к опыту",
        xp_change=100,
    )
    location_side_effect = SideEffect(
        name="Атмосфера в регистраутре",
        description="Атмосфера отчаяния в регистраутре подействовала на вас",
        hp_change=-1,
        strength_change=-1,
    )

    registration_room = Location(
        name="Регистратура",
        description="Ваше первое испытание",
        side_effect=location_side_effect,
    )

    npc1 = NPC(
        name="Медсестра Иришка Чики-Пики",
        description="Злая тетка, которая работает в регистратуре",
        start_phrase="Что у вас?",
        end_phrase="Следующий!",
        location=registration_room,
    )
    npc2 = NPC(
        name="Терапевт Федор",
        description="Это терапевт, он скажет, каких врачей нужно пройти для медосмотра",
        start_phrase="Здраствуйте, проходите. Вы на медосмотр?",
        end_phrase="Вот ваше список врачей которых нужно посетить!",
        xp=100,
        location=registration_room,
    )

    enemy = Enemy(
        name="Какая-то бабка",
        description="Это ваш первый противник. Стоит в очереди и не дает вам пройти",
        start_phrase="Ты что сквозь очередь лезешь?",
        end_phrase="Ну и молодежь пошла!",
        location=registration_room,
    )

    phrase = Phrase(phrase="Дебил!", enemy=enemy)

    sandwich = Item(name="Бутреброд", description="Это же бутерброд!", npc=enemy)

    quest = Quest(
        name="Иди к терапевту",
        description="Терапевт даст направление с врачами, которые ты посетил",
        side_effect=quest_side_effect,
        npc=npc1,
        required_npcs=[npc2],
    )
    session.add_all(
        (
            location_side_effect,
            location_side_effect,
            registration_room,
            npc1,
            npc2,
            enemy,
            phrase,
            sandwich,
            quest,
        )
    )
    session.commit()


def test_create_tables(create_tables):
    pass


def test_add_data(add_data):
    pass
