import asyncio
from get_to_the_clinic_game.entities import Game
from get_to_the_clinic_game.orm.orm import Character, Location, Quest


async def main():
    game = Game()

    if not await game.protagonist_exists(id=1):
        await game.create_protagonist(id=1, name="Aboba")

    print(await Location.get_full_info_location(location_id=1, protagonist_id=1))

    for i in await Location.get_characters_on_location(1, 1):
        print(i.id, i.name, i.description)

    print(await Quest.get_full_quest_info(1))


    # print(await Character.get_full_character_info(character_id=2))


if __name__ == "__main__":
    asyncio.run(main())
