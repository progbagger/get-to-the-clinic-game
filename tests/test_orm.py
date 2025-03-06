import pytest
from typing import AsyncGenerator
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from get_to_the_clinic_game.orm.database import DatabaseManager
from get_to_the_clinic_game.orm import (
    Base,
    SideEffect,
    Location,
    Character,
    NPC,
    Enemy,
    Protagonist,
    Phrase,
    Item,
    Quest,
)

from get_to_the_clinic_game.services import (
    ProtagonistService,
    LocationService,
    CharacterService,
    QuestService,
    ItemService,
)


@pytest.fixture(autouse=True)
async def session() -> AsyncGenerator[AsyncSession, None]:
    database = DatabaseManager("sqlite+aiosqlite:///:memory:")
    await database.create_tables()
    async with database.get_session() as s:
        yield s


@pytest.fixture
async def side_effects(session: AsyncSession) -> list[SideEffect]:
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
            name="Атмосфера страха",
            description="Атмосфера страха в коридоре, в ожидании неизбежного",
            strength_change=-2,
            xp_change=-3,
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
    session.add_all(side_effects)
    await session.commit()

    return side_effects


@pytest.fixture
async def locations(
    side_effects: list[SideEffect], session: AsyncSession
) -> list[Location]:
    locations = [
        Location(
            name="Регистратура",
            description="Ваша начальная локация",
            side_effect=side_effects[1],
        ),
        Location(
            name="Коридор страха",
            description="Бесконечный коридор, котррый ведет в ад.",
            side_effect=side_effects[2],
        ),
        Location(
            name="Кабинет терапевта",
            description="Тут все проверяют",
        ),
    ]
    locations[0].id = 1
    locations[1].id = 2
    locations[2].id = 3

    locations[0].neighbour_locations.append(locations[1])
    locations[1].neighbour_locations.append(locations[0])
    locations[1].neighbour_locations.append(locations[2])
    locations[2].neighbour_locations.append(locations[1])

    session.add_all(locations)
    await session.commit()

    return locations


@pytest.fixture
async def npcs(locations: list[Location], session: AsyncSession) -> list[NPC]:
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
            location=locations[2],
        ),
    ]
    session.add_all(npcs)
    await session.commit()

    return npcs


@pytest.fixture
async def enemies(locations: list[Location], session: AsyncSession) -> list[Enemy]:

    enemies = [
        Enemy(
            name="Баба Вера",
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

    session.add_all(enemies)
    await session.commit()

    return enemies


@pytest.fixture
async def items(
    enemies: list[Enemy],
    locations: list[Location],
    side_effects: list[SideEffect],
    session: AsyncSession,
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
            name="Сигареты здоровья",
            description="Это великие сигареты здоровья! Курите каждый день по пачке в день и будете здоровыми :р Всем советую!",
            location=locations[1],
        ),
    ]

    session.add_all(items)
    await session.commit()

    return items


@pytest.fixture
async def quests(
    npcs: list[NPC], side_effects: list[SideEffect], session: AsyncSession
) -> list[Quest]:
    quests = [
        Quest(
            name="Иди к терапевту",
            description="Терапевт даст направление с врачами, которые тебе нужно посетить",
            side_effect=side_effects[0],
            npc=npcs[0],
            required_npcs=[npcs[1]],
        )
    ]
    session.add_all(quests)
    await session.commit()

    return quests


async def test_side_effects(side_effects: list[SideEffect], session: AsyncSession):
    result = (await session.scalars(select(SideEffect))).all()

    assert side_effects == result


async def test_locations(locations: list[Location], session: AsyncSession):
    result = (await session.scalars(select(Location))).all()

    assert locations == result


@pytest.mark.parametrize("location_id", [1, 2, 3])
async def test_get_neighbour_locations(
    locations: list[Location], session: AsyncSession, location_id
):
    result = await LocationService.get_neighbour_locations(location_id)

    assert sorted(
        locations[location_id - 1].neighbour_locations, key=lambda x: x.id
    ) == sorted(result, key=lambda x: x.id)


@pytest.mark.parametrize("location_id", [1, 2, 3])
async def test_get_characters_by_location(
    locations: list[Location],
    npcs: list[NPC],
    enemies: list[Enemy],
    session: AsyncSession,
    location_id: list[int],
):

    result = await LocationService.get_characters_by_location(location_id, 1)

    assert locations[location_id - 1].characters == result


@pytest.mark.parametrize("location_id", [1, 2, 3])
async def test_get_items_by_location(
    locations: list[Location],
    items: list[Item],
    session: AsyncSession,
    location_id: list[int],
):
    result = await LocationService.get_items_by_location(location_id, 1)

    assert locations[location_id - 1].items == result


@pytest.mark.parametrize("location_id", [1, 2, 3])
async def test_get_location_detail(
    locations: list[Location],
    npcs: list[NPC],
    enemies: list[Enemy],
    items: list[Item],
    session: AsyncSession,
    location_id: list[int],
):
    result = await LocationService.get_location_details(location_id, 1)

    assert locations[location_id - 1] == result


async def test_npcs(npcs: list[NPC], session: AsyncSession):
    result = (await session.scalars(select(NPC))).all()

    assert npcs == result


async def test_enemies(enemies: list[Enemy], session: AsyncSession):
    result = (await session.scalars(select(Enemy))).all()

    assert enemies == result


async def test_items(items: list[Item], session: AsyncSession):
    result = (await session.scalars(select(Item))).all()

    assert items == result


async def test_quests(quests: list[Quest], session: AsyncSession):
    result = (await session.scalars(select(Quest))).all()

    assert quests == result


# async def test_get_protogonist(locations: list[Location], session: AsyncSession):

#     session.add_all(locations)
#     await session.commit()
