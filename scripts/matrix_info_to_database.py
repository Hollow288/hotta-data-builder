import asyncio
import json
import os

from tortoise import Tortoise

from config import database_config
from models import SuitUnactivateDetail
from models.matrix import Matrix


async def matrix_info_to_database():
    # 初始化数据库
    await Tortoise.init(
        config=database_config.TORTOISE_ORM
    )

    matrix_json_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "dist/final", "matrix.json"))

    with open(matrix_json_path, "r", encoding="utf-8") as f:
        matrix_json = json.load(f)

    for name, data in matrix_json.items():

        matrix_obj = await Matrix.create(
            matrix_key=name,
            suit_name=data['SuitName'],
            matrix_suit_quality=data['MatrixSuitQuality'],
            suit_icon=data['SuitIcon']
        )

        for detail_name, detail_desc in data['SuitUnactivateDetail'].items():
            await SuitUnactivateDetail.create(
                matrix_id=matrix_obj.matrix_id,
                item_name=detail_name,
                item_describe=detail_desc
            )
