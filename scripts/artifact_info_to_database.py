import asyncio
import json
import os

from tortoise import Tortoise

from config import database_config
from models import ArtifactData


async def artifact_info_to_database():
    # 初始化数据库
    # await Tortoise.init(
    #     config=database_config.TORTOISE_ORM
    # )

    artifact_json_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "dist/final", "artifact_data.json"))

    with open(artifact_json_path, "r", encoding="utf-8") as f:
        artifact_json = json.load(f)

    for name, data in artifact_json.items():

        await ArtifactData.create(
            food_key=name,
            artifact_key=data['artifact_key'],
            item_rarity=data['item_rarity'],
            item_name=data['item_name'],
            card_image=data['card_image'],
            use_description=data['use_description'],
            artifact_attribute_data=data['artifact_attribute_data']

        )
