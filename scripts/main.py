import asyncio

from config import database_config
from scripts.food_info_to_database import food_info_to_database
from scripts.make_cook_recipes import make_cook_recipes
from scripts.make_food_screenshots import make_all_food_image
from scripts.make_game_json import generate_game_json
from scripts.make_matrix import make_matrix
from scripts.make_matrix_screenshots import make_all_matrix_image
from scripts.make_recipes_screenshots import make_all_recipes_image
from scripts.make_weapons import make_weapons
from tortoise import Tortoise

from scripts.make_weapons_screenshots import make_all_weapons_image
from scripts.make_weapons_skill_screenshots import make_all_weapons_skill_image
from scripts.matrix_info_to_database import matrix_info_to_database
from scripts.recipes_info_to_database import recipes_info_to_database
from scripts.weapons_info_to_database import weapons_info_to_database


async def main():

    await Tortoise.init(
        config=database_config.TORTOISE_ORM
    )

    # await generate_game_json()
    # await make_matrix()
    # await make_weapons()
    # await make_cook_recipes()
    #
    #
    # await food_info_to_database()
    # await recipes_info_to_database()
    # await matrix_info_to_database()
    # await weapons_info_to_database()

    await make_all_recipes_image()
    await make_all_food_image()
    await make_all_matrix_image()
    await make_all_weapons_image()
    await make_all_weapons_skill_image()


if __name__ == "__main__":
    asyncio.run(main())
