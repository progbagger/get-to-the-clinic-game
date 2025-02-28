import asyncio
from get_to_the_clinic_game.entities import Game
from get_to_the_clinic_game.orm.orm import Character, Enemy, Location, Quest, Item


async def main():
    game = Game()

    if not await game.protagonist_exists(id=1):
        await game.create_protagonist(id=1, name="Aboba")

    print(await Location.get_full_info_location(location_id=3, protagonist_id=1))

    # print(await Character.get_full_character_info(character_id=2))

    print(await Item.get_full_item_info(1))
    print(await Character.get_full_character_info(1))
    print(await Enemy.get_enemy_items(1))


if __name__ == "__main__":
    asyncio.run(main())
