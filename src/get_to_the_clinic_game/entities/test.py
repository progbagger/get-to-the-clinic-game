import asyncio
from get_to_the_clinic_game.entities import Game


async def main():
    game = Game()

    if await game.protagonist_exists(id=1):
        await game.load_protagonist(id=1)
    else:
        await game.create_protagonist(id=1, name="Aboba")

    print(
        game.protagonist.id,
        game.protagonist.name,
        game.protagonist.location_id,
    )

    cur_location = await game.protagonist.whereami()
    print(cur_location.name, cur_location.description)


if __name__ == "__main__":
    asyncio.run(main())

# cur_location = game.protagonist.whereami()
# cur_location.side_effect.apply(protagonist=game.protagonist.protagonist)
# print(game.protagonist.protagonist.hp, game.protagonist.protagonist.strength)
# cur_location.side_effect.cancel(protagonist=game.protagonist.protagonist)
# print(game.protagonist.protagonist.hp, game.protagonist.protagonist.strength)

# print(cur_location.name, cur_location.description, cur_location.side_effect)

# for character in cur_location.characters:
#     print(character.id, character.name, character.type)
#     character = game.protagonist.talk_to(character_id=character.id)
#     if character.type == "npc":
#         for quest in character.quests:
#             print(quest.name)
#     else:
#         print(character.hp, character.strength)
#         for phrase in character.phrases:
#             print(phrase.phrase)
#         for i in character.items:
#             print(i.name)

# for item in cur_location.items:
#     print(item.id, item.name, item.description)

# for location in game.get_neighbour_locations():
#     print(location.name)

# char = game.protagonist.talk_to(character.id)
# if char.type == "enemy":
#     print(char.name, char.xp)

# for i in game.protagonist.location.characters:
#     print(i.id, i.name)
# print(game.protagonist.talk_to(i.id))
