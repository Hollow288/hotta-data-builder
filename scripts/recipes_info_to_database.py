import asyncio
import json
import os

from tortoise import Tortoise

from config import database_config
from models import SuitUnactivateDetail, CookRecipesDataTable, RecipesFood, FoodData
from models.matrix import Matrix
from utils.minio_client import minio_client


async def recipes_info_to_database():
    # 初始化数据库
    await Tortoise.init(
        config=database_config.TORTOISE_ORM
    )

    recipes_json_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "dist/final", "recipes.json"))

    with open(recipes_json_path, "r", encoding="utf-8") as f:
        recipes_json = json.load(f)

    for name, data in recipes_json.items():

        recipes_obj = await CookRecipesDataTable.create(
            recipes_key=name,
            recipes_name=data['recipes_name'],
            recipes_des=data['recipes_des'],
            categories=data['categories'],
            use_description=data['use_description'],
            buffs=data['buffs'],
            recipes_icon=data['recipes_icon']
        )

        for food_key, amount in data['ingredients'].items():

            food_data = await FoodData.filter(food_key=food_key).first()

            if food_data is None:
                print(f"入库{recipes_obj.recipes_name}时,食材 {food_key} 未收录!")
            else:

                await RecipesFood.create(
                    food_id=food_data.food_id,
                    recipes_id=recipes_obj.recipes_id,
                    amount=amount
                )
