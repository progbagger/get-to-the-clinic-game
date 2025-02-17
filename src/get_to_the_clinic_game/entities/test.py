import asyncio
from get_to_the_clinic_game.entities import Game
from get_to_the_clinic_game.orm.orm import Character, Location


async def main():
    game = Game()

    if not await game.protagonist_exists(id=1):
        await game.create_protagonist(id=1, name="Aboba")

    print(await Location.get_full_info_location(location_id=1, protagonist_id=1))

    for i in await Location.get_all_characters_on_location(1, 1):
        print(i.id, i.name, i.description)


if __name__ == "__main__":
    asyncio.run(main())
