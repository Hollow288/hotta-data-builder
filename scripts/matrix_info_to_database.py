import asyncio
import json
import os

from tortoise import Tortoise

from config import database_config
from models import SuitUnactivateDetail
from models.matrix import Matrix
from utils.minio_client import minio_client


async def to_do():
    # 初始化数据库
    await Tortoise.init(
        config=database_config.TORTOISE_ORM
    )

    matrix_json_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "dist/final", "matrix.json"))

    with open(matrix_json_path, "r", encoding="utf-8") as f:
        matrix_json = json.load(f)

    for name, data in matrix_json.items():

        minio_url = ''

        local_icon_path = data['SuitIcon']
        if local_icon_path and os.path.exists(local_icon_path):
            bucket_name = 'hotta-matrix-icon'
            object_name = f"{os.path.basename(local_icon_path)}"

            if not minio_client.bucket_exists(bucket_name):
                minio_client.make_bucket(bucket_name)

            # 上传文件
            minio_client.fput_object(bucket_name, object_name, local_icon_path)

            # 生成访问地址（如果你自己部署了域名或用 minio 默认url）
            minio_url = f"{bucket_name}/{object_name}"


        matrix_obj = await Matrix.create(
            matrix_key=name,
            suit_name=data['SuitName'],
            matrix_suit_quality=data['MatrixSuitQuality'],
            suit_icon=minio_url
        )

        for detail_name, detail_desc in data['SuitUnactivateDetail'].items():
            await SuitUnactivateDetail.create(
                matrix_id=matrix_obj.matrix_id,
                item_name=detail_name,
                item_describe=detail_desc
            )


if __name__ == "__main__":
   asyncio.run(to_do())