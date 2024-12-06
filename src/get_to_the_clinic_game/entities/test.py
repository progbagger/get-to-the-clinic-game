from get_to_the_clinic_game.entities import Game


if __name__ == "__main__":
    game = Game("sqlite:///db.db")
    if game.protagonist_exists(1):
        game.load_game(1)
    else:
        game.create_game(1, "Aboba")

    print("1")
    print(game.cur_location())

    for i in game.protagonist.location.characters:
        print(i.name, i.description)
