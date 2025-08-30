import asyncio
import json
import os

from tortoise import Tortoise

from config import database_config
from models import Weapons, WeaponSensualityLevelData, WeaponUpgradeStarPack, WeaponSkill
from utils.minio_client import minio_client


async def weapons_info_to_database():
    # 初始化数据库
    # await Tortoise.init(
    #     config=database_config.TORTOISE_ORM
    # )

    weapons_json_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "dist/final", "weapons.json"))

    with open(weapons_json_path, "r", encoding="utf-8") as f:
        weapons_json = json.load(f)

    for name, data in weapons_json.items():

        # minio_url = ''
        #
        # local_icon_path = data['ItemIcon']
        # if local_icon_path and os.path.exists(local_icon_path):
        #     bucket_name = 'hotta-weapons-icon'
        #     object_name = f"{os.path.basename(local_icon_path)}"
        #
        #     if not minio_client.bucket_exists(bucket_name):
        #         minio_client.make_bucket(bucket_name)
        #
        #     # 上传文件
        #     minio_client.fput_object(bucket_name, object_name, local_icon_path)
        #
        #     # 生成访问地址（如果你自己部署了域名或用 minio 默认url）
        #     minio_url = f"{bucket_name}/{object_name}"

        weapons_obj = await Weapons.create(
            item_key=name,
            item_name=data['ItemName'],
            item_rarity=data['ItemRarity'],
            weapon_category=data['WeaponCategory'],
            weapon_element_type=data['WeaponElement']['WeaponElementType'],
            weapon_element_name=data['WeaponElement']['WeaponElementName'],
            weapon_element_desc=data['WeaponElement']['WeaponElementDesc'],
            armor_broken=data['ArmorBroken'],
            charging=data['Charging'],
            item_icon=data['ItemIcon'],
            description=data['Description'],
            remould_detail=data['RemouldDetail']
        )

        for index, item in enumerate(data['WeaponSensualityLevelData']):
            await WeaponSensualityLevelData.create(
                weapons_id=weapons_obj.weapons_id,
                item_name=f"通感{index+1}星",
                item_describe=item
            )

        for index, item in enumerate(data['WeaponUpgradeStarPack']):
            await WeaponUpgradeStarPack.create(
                weapons_id=weapons_obj.weapons_id,
                item_name=f"进阶{index+1}星",
                item_describe=item
            )

        for skill_data in data['WeaponSkill']:
            await WeaponSkill.create(
                weapons_id=weapons_obj.weapons_id,
                skill_type=skill_data['type'],
                icon = skill_data['icon'],
                item_name=skill_data['name'],
                item_describe=skill_data['des']
            )
