import asyncio

from scripts.data.make_artifact_data import make_artifact_data
from scripts.data.make_cook_recipes import make_cook_recipes
from scripts.data.make_fashion_data import make_fashion_data
from scripts.data.make_game_json import generate_game_json
from scripts.data.make_matrix import make_matrix
from scripts.data.make_weapons import make_weapons
from scripts.screenshots.make_artifact_screenshots import make_all_artifact_image
from scripts.screenshots.make_fashion_screenshots import make_all_fashion_image
from scripts.screenshots.make_food_screenshots import make_all_food_image
from scripts.screenshots.make_matrix_screenshots import make_all_matrix_image
from scripts.screenshots.make_recipes_screenshots import make_all_recipes_image
from scripts.screenshots.make_weapons_screenshots import make_all_weapons_image
from scripts.screenshots.make_weapons_skill_screenshots import make_all_weapons_skill_image


async def main():

    #
    # await generate_game_json()
    # await make_matrix()
    # await make_weapons()
    # await make_cook_recipes()
    # await make_fashion_data()
    # await make_artifact_data()
    #

    # await make_all_recipes_image()
    # await make_all_food_image()
    await make_all_matrix_image()
    # await make_all_weapons_image()
    # await make_all_weapons_skill_image()
    # await make_all_fashion_image()
    # await make_all_artifact_image()


if __name__ == "__main__":
    asyncio.run(main())
