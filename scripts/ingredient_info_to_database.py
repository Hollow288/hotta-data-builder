import asyncio
import json
import os

from tortoise import Tortoise

from config import database_config
from models import SuitUnactivateDetail, IngredientData
from models.matrix import Matrix
from utils.cook_utils import fix_ingredient_icon_url
from utils.minio_client import minio_client


async def to_do():
    # 初始化数据库
    await Tortoise.init(
        config=database_config.TORTOISE_ORM
    )

    ingredient_json_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "dist/final", "ingredient.json"))

    with open(ingredient_json_path, "r", encoding="utf-8") as f:
        ingredient_json = json.load(f)

    for name, data in ingredient_json.items():

        minio_url = ''

        local_icon_path = data['ingredient_icon']
        if fix_ingredient_icon_url(local_icon_path) is not None:

            bucket_name = 'hotta-ingredient-icon'
            object_name = f"{os.path.basename(local_icon_path)}"

            if not minio_client.bucket_exists(bucket_name):
                minio_client.make_bucket(bucket_name)

            # 上传文件
            minio_client.fput_object(bucket_name, object_name, fix_ingredient_icon_url(local_icon_path))

            # 生成访问地址（如果你自己部署了域名或用 minio 默认url）
            minio_url = f"{bucket_name}/{object_name}"


        await IngredientData.create(
            ingredient_key=name,
            ingredient_name=data['ingredient_name'],
            ingredient_des=data['ingredient_des'],
            ingredient_icon=minio_url
        )



if __name__ == "__main__":
   asyncio.run(to_do())