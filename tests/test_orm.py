from typing import AsyncGenerator
import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from get_to_the_clinic_game.orm.database import test_db_manager as db_manager
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


@pytest.fixture(autouse=True)
async def create_tables():
    await db_manager.create_tables()


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
            description="Это великие сигареты здоровья! Курите каждый день по пачке в день и будете здоровыми :р Всем советую!",
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


async def test_side_effects(side_effects: list[SideEffect]):
    async with db_manager.get_session() as session:
        session.add_all(side_effects)
        await session.commit()

        assert side_effects == (await session.scalars(select(SideEffect))).all()


async def test_locations(locations: list[Location]):
    async with db_manager.get_session() as session:
        session.add_all(locations)
        await session.commit()

        assert locations == (await session.scalars(select(Location))).all()
        assert locations[1].items == (await session.scalars(select(Item))).all()


async def test_npcs(npcs: list[NPC]):
    async with db_manager.get_session() as session:
        session.add_all(npcs)
        await session.commit()

        assert npcs == (await session.scalars(select(NPC))).all()


async def test_enemies(enemies: list[Enemy]):
    async with db_manager.get_session() as session:
        session.add_all(enemies)
        await session.commit()

        assert enemies == (await session.scalars(select(Enemy))).all()


async def test_items(items: list[Item]):
    async with db_manager.get_session() as session:
        session.add_all(items)
        await session.commit()

        assert items == (await session.scalars(select(Item))).all()


async def test_quests(quests: list[Quest]):
    async with db_manager.get_session() as session:
        session.add_all(quests)
        await session.commit()

        assert quests == (await session.scalars(select(Quest))).all()


async def test_get_protogonist(locations: list[Location]):
    async with db_manager.get_session() as session:
        session.add_all(locations)
        await session.commit()

        assert quests == (await session.scalars(select(Quest))).all()
