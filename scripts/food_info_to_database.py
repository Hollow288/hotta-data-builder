import asyncio
import json
import os

from tortoise import Tortoise

from config import database_config
from models import FoodData
from utils.cook_utils import fix_food_icon_url
from utils.minio_client import minio_client


async def to_do():
    # 初始化数据库
    await Tortoise.init(
        config=database_config.TORTOISE_ORM
    )

    food_json_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "dist/final", "food.json"))

    with open(food_json_path, "r", encoding="utf-8") as f:
        food_json = json.load(f)

    for name, data in food_json.items():

        minio_url = ''

        local_icon_path = data['food_icon']
        if fix_food_icon_url(local_icon_path) is not None:

            bucket_name = 'hotta-food-icon'
            object_name = f"{os.path.basename(local_icon_path)}"

            if not minio_client.bucket_exists(bucket_name):
                minio_client.make_bucket(bucket_name)

            # 上传文件
            minio_client.fput_object(bucket_name, object_name, fix_food_icon_url(local_icon_path))

            # 生成访问地址（如果你自己部署了域名或用 minio 默认url）
            minio_url = f"{bucket_name}/{object_name}"


        await FoodData.create(
            food_key=name,
            food_name=data['food_name'],
            food_des=data['food_des'],
            food_source=data['food_source'],
            food_icon=minio_url,
            use_description=data['use_description'],
            buffs=data['buffs']

        )



if __name__ == "__main__":
   asyncio.run(to_do())