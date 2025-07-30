import os
import shutil
from pathlib import Path

from dotenv import load_dotenv
import json

from utils.common_utils import extract_tail_name, resolve_resource_path, make_remould_detail
from utils.weapons_utils import translate_weapon_info, make_element_desc_name, extract_series_values, make_weapon_skill, \
    make_upgrade_star_pack

# 加载 .env 文件
load_dotenv()

# 原数据目录
source_path = os.getenv("SOURCE_PATH")

# 武器列表起点文件目录
static_weapon_data_table_path = os.getenv("STATIC_WEAPON_DATA_TABLE") or os.path.join(
    source_path, "CoreBlueprints/DataTable/StaticWeaponDataTable.json"
)

# 武器星级效果信息
weapon_upgrade_star_data_path = os.getenv("WEAPON_UPGRADE_STAR_DATA") or os.path.join(
    source_path, "CoreBlueprints/DataTable/WeaponUpgradeStarData.json"
)

# 武器通感效果信息
weapon_sensuality_level_data_path = os.getenv("WEAPON_SENSUALITY_LEVEL_DATA") or os.path.join(
    source_path, "CoreBlueprints/DataTable/WeaponData/DT_WeaponSensualityLevelData.json"
)

# 武器属性信息
equip_batch_level_static_data_table_path = os.getenv("EQUIP_BATCH_LEVEL_STATIC_DATA_TABLE") or os.path.join(
    source_path, "CoreBlueprints/DataTable/EquipBatchLevelStaticDataTable.json"
)

# 武器技能信息
gameplay_ability_tips_data_table_path = os.getenv("GAMEPLAY_ABILITY_TIPS_DATA_TABLE") or os.path.join(
    source_path, "CoreBlueprints/DataTable/GameplayAbilityTipsDataTable.json"
)

# 武器技能数值信息
skill_update_tips_path = os.getenv("SKILL_UPDATE_TIPS") or os.path.join(
    source_path, "CoreBlueprints/DataTable/Skill/SkillUpdateTips.json"
)

# Game.json文件目录
game_json_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "dist/intermediate", "Game.json"))

if __name__ == "__main__":
    with open(static_weapon_data_table_path, "r", encoding="utf-8") as f:
        static_weapon_data_table = json.load(f)

    with open(game_json_path, "r", encoding="utf-8") as f:
        game_json = json.load(f)

    with open(weapon_upgrade_star_data_path, "r", encoding="utf-8") as f:
        weapon_upgrade_star_data = json.load(f)

    with open(weapon_sensuality_level_data_path, "r", encoding="utf-8") as f:
        weapon_sensuality_level_data = json.load(f)

    with open(equip_batch_level_static_data_table_path, "r", encoding="utf-8") as f:
        equip_batch_level_static_data_table_data = json.load(f)

    with open(gameplay_ability_tips_data_table_path, "r", encoding="utf-8") as f:
        gameplay_ability_tips_data = json.load(f)

    with open(skill_update_tips_path, "r", encoding="utf-8") as f:
        skill_update_tips = json.load(f)

    # 星级效果
    weapon_upgrade_star_data_rows_data = {
        k.lower(): v for k, v in weapon_upgrade_star_data[0].get("Rows", {}).items()
    }

    # 通感效果
    weapon_sensuality_level_data_rows_data = weapon_sensuality_level_data[0].get("Rows", {})

    # 找出仓库武器
    static_weapon_data_table_rows_data = static_weapon_data_table[0].get("Rows", {})

    # 武器特质数值
    quip_batch_level_static_data_table_rows_data = equip_batch_level_static_data_table_data[0].get("Rows", {})

    # 武器技能信息
    gameplay_ability_tips_data_rows_data = gameplay_ability_tips_data[0].get("Rows", {})

    # 武器技能数值信息
    skill_update_tips_rows_data = skill_update_tips[0].get("Rows", {})

    warehouse_weapons = {
        name: data
        for name, data in static_weapon_data_table_rows_data.items()
        if data.get("IsWarehouseWeapon") == True
    }

    # 保存一下过滤后的json 可能会用到 warehouse_weapons将作为我们处理的武器列表起点
    output_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "dist/intermediate", "weapons_filtered.json"))
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(warehouse_weapons, f, ensure_ascii=False, indent=2)

    result_weapons_dict = {}

    for name, data in warehouse_weapons.items():
        # 一些基本信息
        some_base_info = weapon_upgrade_star_data_rows_data[(data['UpgradeStarPackID'] + '_0').lower()]

        # 临时字典
        weapons_info = {
            'ItemName': game_json[extract_tail_name(data['ItemName']['TableId'])][data['ItemName']['Key']],
            'ItemIcon': resolve_resource_path(data['ItemIcon']['AssetPathName'], '.png'),
            'ItemRarity': translate_weapon_info(data['ItemRarity']),
            'WeaponCategory': translate_weapon_info(data['WeaponTypeData']['WeaponCategory']),

            "WeaponElement": {'WeaponElementType': translate_weapon_info(data['WeaponTypeData']['WeaponElementType'],
                                                                         data['WeaponTypeData'][
                                                                             'WeaponAccessoryElementType']),
                              "WeaponElementName": make_element_desc_name(data['ItemRarity'],
                                                                          data['WeaponTypeData']['WeaponElementType'],
                                                                          data['WeaponTypeData'][
                                                                              'WeaponAccessoryElementType'],
                                                                          quip_batch_level_static_data_table_rows_data,
                                                                          game_json)['element_name'],
                              "WeaponElementDesc": make_element_desc_name(data['ItemRarity'],
                                                                          data['WeaponTypeData']['WeaponElementType'],
                                                                          data['WeaponTypeData'][
                                                                              'WeaponAccessoryElementType'],
                                                                          quip_batch_level_static_data_table_rows_data,
                                                                          game_json)['element_desc']
                              },
            'ArmorBroken': some_base_info['ArmorBroken'],
            'Charging': some_base_info['Charging'],
            'Description': game_json[extract_tail_name(data['Description']['TableId'])][data['Description']['Key']],
            "RemouldDetail": make_remould_detail(some_base_info, game_json),
            "WeaponSensualityLevelData": extract_series_values(weapon_sensuality_level_data_rows_data,
                                                               data['SensualityPackId'], game_json),
            "UpgradeStarPack": make_upgrade_star_pack(data['UpgradeStarPackID'].lower(), data['MaxUpgradeStar'],
                                                      game_json, weapon_upgrade_star_data_rows_data),
            "WeaponSkill": make_weapon_skill(data['WeaponSkillList'], gameplay_ability_tips_data_rows_data,
                                             skill_update_tips_rows_data, game_json)
        }

        # print("最终 WeaponSensualityLevelData：", weapons_info["WeaponSensualityLevelData"])
        result_weapons_dict[name] = weapons_info

    # 最终保存
    output_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "dist/final", "weapons.json"))
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result_weapons_dict, f, ensure_ascii=False, indent=2)

    base_output_dir = Path(__file__).resolve().parent.parent / 'dist'

    for key, item in result_weapons_dict.items():
        icon_path = item.get("ItemIcon")
        if not icon_path or not os.path.isfile(icon_path):
            print(f"图标文件不存在: {icon_path}")
            continue

        # 从 Hotta 开始的相对路径
        parts = Path(icon_path).parts
        try:
            hotta_index = parts.index("Hotta")
        except ValueError:
            print(f"无法识别 Hotta 路径: {icon_path}")
            continue

        relative_path = Path(*parts[hotta_index:])
        target_path = base_output_dir / relative_path

        # 创建目标目录
        target_path.parent.mkdir(parents=True, exist_ok=True)

        # 执行复制
        shutil.copy2(icon_path, target_path)
