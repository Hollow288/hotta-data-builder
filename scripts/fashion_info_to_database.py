import asyncio
import json
import os

from tortoise import Tortoise

from config import database_config
from models import FoodData
from models.fashion_data import FashionData


async def fashion_info_to_database():
    # 初始化数据库
    await Tortoise.init(
        config=database_config.TORTOISE_ORM
    )

    fashion_json_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "dist/final", "fashion_data.json"))

    with open(fashion_json_path, "r", encoding="utf-8") as f:
        fashion_json = json.load(f)

    for name, data in fashion_json.items():

        await FashionData.create(
            fashion_key=data['fashion_key'],
            fashion_name=data['fashion_Name'],
            description=data['Description'],
            active_source=data['ActiveSource'],
            icons=data['Icons']
        )
