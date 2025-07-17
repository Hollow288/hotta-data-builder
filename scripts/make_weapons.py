import os
from dotenv import load_dotenv
import json

from utils import extract_tail_name, translate_weapon_info, resolve_resource_path

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

# Game.json文件目录
game_json_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "dist/intermediate", "Game.json"))



def make_remould_detail(parms_some_base_info: dict,parms_game_json :dict):
    if parms_some_base_info.get('RemouldDetail', {}).get('Key'):
        source_string = parms_game_json[extract_tail_name(parms_some_base_info['RemouldDetail']['TableId'])][parms_some_base_info['RemouldDetail']['Key']]

        # 处理数值部分
        remould_detail_params_list = parms_some_base_info['RemouldDetailParams']

        result_remould_numeric_list = []

        for remould_detail_params in remould_detail_params_list:
            resolve_path = resolve_resource_path(remould_detail_params['Curve']['CurveTable']['ObjectPath'])
            with open(resolve_path, "r", encoding="utf-8") as nj:
                numeric_json = json.load(nj)

            numeric_key_val = numeric_json[0].get("Rows", {})

            result_remould_numeric_list.append(numeric_key_val[remould_detail_params['Curve']['RowName']]['Keys'][0]['Value'] * remould_detail_params['Value'])


        print(source_string)
        print(result_remould_numeric_list)
        return source_string
    else :
        return None





if __name__ == "__main__":
    with open(static_weapon_data_table_path, "r", encoding="utf-8") as f:
        static_weapon_data_table = json.load(f)

    with open(game_json_path, "r", encoding="utf-8") as f:
        game_json = json.load(f)

    with open(weapon_upgrade_star_data_path, "r", encoding="utf-8") as f:
        weapon_upgrade_star_data = json.load(f)

    # 星级效果
    weapon_upgrade_star_data_rows_data = {
        k.lower(): v for k, v in weapon_upgrade_star_data[0].get("Rows", {}).items()
    }


    # 找出仓库武器
    static_weapon_data_table_rows_data = static_weapon_data_table[0].get("Rows", {})

    warehouse_weapons = {
        name: data
        for name, data in static_weapon_data_table_rows_data.items()
        if data.get("IsWarehouseWeapon") == True
    }



    # 找出仓库武器
    static_weapon_data_table_rows_data = static_weapon_data_table[0].get("Rows", {})

    # 保存一下过滤后的json 可能会用到 warehouse_weapons将作为我们处理的武器列表起点
    output_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "dist/intermediate", "weapons_filtered.json"))
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(warehouse_weapons, f, ensure_ascii=False, indent=2)

    result_weapons_dict = {}

    for name, data in warehouse_weapons.items():

        # 一些基本信息
        some_base_info = weapon_upgrade_star_data_rows_data[(data['UpgradeStarPackID'] + '_0').lower()]

        # 临时字典
        weapons_info = {
            'ItemName': game_json[extract_tail_name(data['ItemName']['TableId'])][data['ItemName']['Key']],
            'ItemRarity': translate_weapon_info(data['ItemRarity']),
            'WeaponCategory': translate_weapon_info(data['WeaponTypeData']['WeaponCategory']),
            'WeaponElementType':translate_weapon_info(data['WeaponTypeData']['WeaponElementType'],data['WeaponTypeData']['WeaponAccessoryElementType']),
            'ArmorBroken': some_base_info['ArmorBroken'],
            'Charging': some_base_info['Charging'],
            'Description': game_json[extract_tail_name(data['Description']['TableId'])][data['Description']['Key']],
            "RemouldDetail": make_remould_detail(some_base_info,game_json)

        }

        result_weapons_dict[name] = weapons_info


    # 最终保存
    output_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "dist/final", "weapons.json"))
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result_weapons_dict, f, ensure_ascii=False, indent=2)






