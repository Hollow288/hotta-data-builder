import asyncio

from config import database_config
from scripts.artifact_info_to_database import artifact_info_to_database
from scripts.fashion_info_to_database import fashion_info_to_database
from scripts.food_info_to_database import food_info_to_database
from scripts.make_artifact_data import make_artifact_data
from scripts.make_artifact_screenshots import make_all_artifact_image
from scripts.make_cook_recipes import make_cook_recipes
from scripts.make_fashion_data import make_fashion_data
from scripts.make_fashion_screenshots import make_all_fashion_image
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

    # tables = ["weapons", "weapon_upgrade_star_pack", "weapon_skill",
    #           "weapon_sensuality_level_data","matrix","suit_unactivate_detail",
    #           "food_data_table","cook_recipes_data_table","recipes_food","fashion_data","artifact_data"]
    #
    # for table in tables:
    #     await Tortoise.get_connection('default').execute_script(f"TRUNCATE TABLE {table}")
    #
    # await generate_game_json()
    # await make_matrix()
    # await make_weapons()
    # await make_cook_recipes()
    # await make_fashion_data()
    await make_artifact_data()
    #
    #
    # await food_info_to_database()
    # await recipes_info_to_database()
    # await matrix_info_to_database()
    # await weapons_info_to_database()
    # await fashion_info_to_database()
    await artifact_info_to_database()

    # await make_all_recipes_image()
    # await make_all_food_image()
    # await make_all_matrix_image()
    # await make_all_weapons_image()
    # await make_all_weapons_skill_image()
    # await make_all_fashion_image()
    await make_all_artifact_image()


if __name__ == "__main__":
    asyncio.run(main())
