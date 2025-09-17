import asyncio
import json
import os
from motor.motor_asyncio import AsyncIOMotorClient

from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()

mongo_uri_config = os.getenv("MONGO_URI")
db_name_config = os.getenv("DB_NAME")

BATCH_SIZE = 1000  # 可根据实际调整

async def import_json_to_mongo(file_path: str, db_name: str, mongo_uri: str):
    client = AsyncIOMotorClient(mongo_uri)
    db = client[db_name]

    # 集合名取文件名去掉后缀
    collection_name = os.path.splitext(os.path.basename(file_path))[0]

    # 先删除集合（如果存在）
    if collection_name in await db.list_collection_names():
        await db[collection_name].drop()
        print(f"集合 '{collection_name}' 已删除，准备重新导入")

    # 读取 JSON 文件
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # 如果是列表，直接存为文档；否则包成列表
    documents = data if isinstance(data, list) else [data]

    # 分批插入
    for i in range(0, len(documents), BATCH_SIZE):
        batch = documents[i:i+BATCH_SIZE]
        if batch:  # 避免空批次
            result = await db[collection_name].insert_many(batch)
            print(f"集合 '{collection_name}' 插入 {len(result.inserted_ids)} 条文档 ({i}~{i+len(batch)-1})")

async def import_multiple_files(file_paths, db_name, mongo_uri):
    for file_path in file_paths:
        await import_json_to_mongo(file_path, db_name, mongo_uri)

# 调用示例
if __name__ == "__main__":
    files = [
        "C:/XM/MY/hotta-data-builder/dist/final/artifact.json",
        "C:/XM/MY/hotta-data-builder/dist/final/fashion.json",
        "C:/XM/MY/hotta-data-builder/dist/final/food.json",
        "C:/XM/MY/hotta-data-builder/dist/final/matrix.json",
        "C:/XM/MY/hotta-data-builder/dist/final/recipes.json",
        "C:/XM/MY/hotta-data-builder/dist/final/weapons.json"
    ]

    asyncio.run(import_multiple_files(
        file_paths=files,
        db_name=db_name_config,
        mongo_uri=mongo_uri_config
    ))









