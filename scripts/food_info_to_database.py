import asyncio
import json
import os

from tortoise import Tortoise

from config import database_config
from models import FoodData


async def food_info_to_database():
    # 初始化数据库
    # await Tortoise.init(
    #     config=database_config.TORTOISE_ORM
    # )

    food_json_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "dist/final", "food.json"))

    with open(food_json_path, "r", encoding="utf-8") as f:
        food_json = json.load(f)

    for name, data in food_json.items():

        await FoodData.create(
            food_key=name,
            food_name=data['food_name'],
            food_des=data['food_des'],
            food_source=data['food_source'],
            food_icon=data['food_icon'],
            use_description=data['use_description'],
            buffs=data['buffs']

        )
