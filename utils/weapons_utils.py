import json
import os
import shutil
from pathlib import Path

from utils.common_utils import extract_tail_name, resolve_resource_path, format_description, make_remould_detail, \
    fix_resolve_resource_path


def extract_series_values(data: dict, base_key: str, game_json: dict) -> list:
    """
    提取以 base_key 为前缀、序号结尾（如 'sense_1', 'sense_2', ...）的字典值，直到找不到为止。单纯用用于武器通感整理

    参数:
        data (dict): 要查找的字典。
        base_key (str): 基础键名（不含下划线和数字）。

    返回:
        list: 所有找到的值组成的列表。
    """

    if base_key == 'None':
        return []

    tem_list = []
    result = []
    index = 1
    while True:
        key = f"{base_key}_{index}"
        if key not in data:
            break
        tem_list.append(data[key])
        index += 1

    for tem in tem_list:
        source_string = game_json[extract_tail_name(tem['RemouldDetail']['TableId'])][tem['RemouldDetail']['Key']]

        remould_detail_params_list = tem['RemouldDetailParams']

        result_remould_numeric_list = []

        for remould_detail_params in remould_detail_params_list:
            resolve_path = resolve_resource_path(remould_detail_params['Curve']['CurveTable']['ObjectPath'])
            with open(resolve_path, "r", encoding="utf-8") as nj:
                numeric_json = json.load(nj)

            numeric_key_val = numeric_json[0].get("Rows", {})

            result_remould_numeric_list.append(
                numeric_key_val[remould_detail_params['Curve']['RowName']]['Keys'][0]['Value'] * remould_detail_params[
                    'Value'])

        results_string = format_description(source_string, result_remould_numeric_list)
        result.append(results_string)

    return result


def make_element_desc_name(item_rarity: str, weapon_element_type: str, weapon_accessory_element_type: int,
                           quip_batch_level_static_data_table_rows_data: dict, game_json: dict) -> dict:
    """
    单纯用于武器属性相关信息的整理
    """

    # weapon_accessory_element_type为0或者1为单属性和异能 雷8 物理4 冰16 火2 为双属性?

    if weapon_accessory_element_type == 0 or weapon_accessory_element_type == 1:
        name_fragment = {
            "EWeaponElementType::Superpower": "32",
            "EWeaponElementType::Physics": "2",
            "EWeaponElementType::Thunder": "16",
            "EWeaponElementType::Flame": "4",
            "EWeaponElementType::Ice": "8"
        }

        # 为什么这里Thunder要对应fire  而Ice对应Thunder才能在EquipBatchLevelStaticDataTable.json找到正确的数值

        quip_batch_find = {
            "EWeaponElementType::Superpower": None,
            "EWeaponElementType::Physics": "Physics",
            "EWeaponElementType::Thunder": "Ice",
            "EWeaponElementType::Flame": "fire",
            "EWeaponElementType::Ice": "Thunder"
        }

    else:

        name_fragment = {
            "EWeaponElementType::Superpower": "32",
            "EWeaponElementType::Physics": "2-4",
            "EWeaponElementType::Thunder": "16-8",
            "EWeaponElementType::Flame": "4-2",
            "EWeaponElementType::Ice": "8-16"
        }

        quip_batch_find = {
            "EWeaponElementType::Superpower": None,
            "EWeaponElementType::Physics": "PhysicsFlame",
            "EWeaponElementType::Thunder": "ThunderIce",
            "EWeaponElementType::Flame": "FlamePhysics",
            "EWeaponElementType::Ice": "IceThunder"
        }

    item_rarity_eff_name = {
        "EItemRarity::ITEM_RARITY_SSR": "2",
        "EItemRarity::ITEM_RARITY_SR": "1",
        "EItemRarity::ITEM_RARITY_R": "0",
    }

    template = game_json['QRSLCommon_ST']["ui_weapon_charge_" + name_fragment[weapon_element_type] + "_desc_0"]

    if weapon_element_type == 'EWeaponElementType::Superpower':
        quip_batch_values = []
    else:
        quip_batch_dict = quip_batch_level_static_data_table_rows_data[
            quip_batch_find[weapon_element_type] + '_' + item_rarity_eff_name[item_rarity]]

        quip_batch_values = [x * 100 for x in quip_batch_dict['GrowUpData'][0]['ParamValues']]

    element_desc = format_description(template, quip_batch_values, 1)

    element_name = game_json['QRSLCommon_ST']['ui_weapon_charge_' + name_fragment[weapon_element_type] + '_0']

    return {"element_desc": element_desc, "element_name": element_name}


def translate_weapon_info(key: str, element_type: int = 0) -> str:
    """
    翻译武器品质和属性，这里只做简单判断，根据WeaponAccessoryElementType是否为0(单属性)
    """

    rarity_map = {
        "EItemRarity::ITEM_RARITY_SSR": "SSR",
        "EItemRarity::ITEM_RARITY_SR": "SR",
        "EItemRarity::ITEM_RARITY_R": "R",
        "EWeaponCategory::DPS": "强攻",
        "EWeaponCategory::Tank": "坚毅",
        "EWeaponCategory::SUP": "恩赐",
        "EWeaponElementType::Superpower": "异能",
        "EWeaponElementType::Physics": "物理",
        "EWeaponElementType::Thunder": "雷电",
        "EWeaponElementType::Flame": "火焰",
        "EWeaponElementType::Ice": "寒冰"
    }

    rarity_map_2 = {
        "EItemRarity::ITEM_RARITY_SSR": "SSR",
        "EItemRarity::ITEM_RARITY_SR": "SR",
        "EItemRarity::ITEM_RARITY_R": "R",
        "EWeaponCategory::DPS": "强攻",
        "EWeaponCategory::Tank": "坚毅",
        "EWeaponCategory::SUP": "恩赐",
        "EWeaponElementType::Superpower": "异能",
        "EWeaponElementType::Physics": "物火",
        "EWeaponElementType::Thunder": "雷冰",
        "EWeaponElementType::Flame": "火物",
        "EWeaponElementType::Ice": "冰雷"
    }

    return (rarity_map_2 if element_type != 0 else rarity_map).get(key, "Unknown")


def make_upgrade_star_pack(upgrade_star_pack_id: str, max_upgrade_star: int, game_json: dict,
                           weapon_upgrade_star_data_rows_data: dict) -> list:
    """
    单纯用来整理武器星级效果

    """

    if max_upgrade_star <= 0:
        return []

    result = []

    filtered_data = {
        f"{upgrade_star_pack_id}_{i}": weapon_upgrade_star_data_rows_data[f"{upgrade_star_pack_id}_{i}"]
        for i in range(1, max_upgrade_star + 1)
        if f"{upgrade_star_pack_id}_{i}" in weapon_upgrade_star_data_rows_data
    }

    for key, value in filtered_data.items():
        # this_start = game_json[extract_tail_name(value['RemouldDetail']['TableId'])][value['RemouldDetail']['Key']]
        result.append(make_remould_detail(value, game_json))

    return result


def make_weapon_skill_desc_value(key: str, ga_parame_num: int, skill_update_tips_rows_data: dict) -> list:
    """
    用于武器技能描述中，将数值数组的等级1数值和原文本组合

    """

    if ga_parame_num <= 0:
        return []

    result = []

    filtered_data = {
        f"{key}_{i}": skill_update_tips_rows_data[f"{key}_{i}"]
        for i in range(1, ga_parame_num + 1)
        if f"{key}_{i}" in skill_update_tips_rows_data
    }

    for key, value in filtered_data.items():
        # Todo 武器等级对于数值的影响

        # 这里只记录技能等级1的状态

        value_at_time_1 = next(
            (item['Value'] for item in value['Keys'] if item['Time'] == 1.0),
            0  # 默认值，防止没有找到时报错
        )

        result.append(value_at_time_1)

    return result


def make_weapon_skill(weapon_skill_list: list, gameplay_ability_tips_data_rows_data: dict,
                      skill_update_tips_rows_data: dict, game_json: dict) -> dict:
    """
    单纯用于武器技能信息整理

    """

    result_weapon_skill = {}

    lowercased_data = {
        k.lower(): v for k, v in gameplay_ability_tips_data_rows_data.items()
    }

    for index, weapon_skill in enumerate(weapon_skill_list):

        weapon_skill = weapon_skill.lower()

        this_type_skill_list = {}

        this_list = lowercased_data[weapon_skill]['GABranchStruct']

        # 这里先不用数据中给出的类型，因为马克武器似乎没有标注，改为使用索引

        # if lowercased_data.get(weapon_skill, {}).get('Name', {}).get('Key') is None:
        #     skill_type = '普攻'
        # else:
        #     skill_type = game_json[extract_tail_name(lowercased_data[weapon_skill]['Name']['TableId'])][lowercased_data[weapon_skill]['Name']['Key']]

        if index == 0:
            skill_type = '普攻'
        elif index == 1:
            skill_type = '闪避'
        elif index == 2:
            skill_type = '技能'
        elif index == 3:
            skill_type = '联携'
        else:
            skill_type = '未知'

        for item in this_list:
            item_name = game_json[extract_tail_name(item['Value']['Name']['TableId'])][item['Value']['Name']['Key']]
            item_desc_tem = game_json[extract_tail_name(item['Value']['Desc']['TableId'])][item['Value']['Desc']['Key']]
            values = make_weapon_skill_desc_value(item['Key'], item['Value']['GAParameNum'],
                                                  skill_update_tips_rows_data)
            item_desc = format_description(item_desc_tem, values)

            this_type_skill_list[item_name] = item_desc

        result_weapon_skill[skill_type] = this_type_skill_list

    return result_weapon_skill


def save_lottery_img(weapon_fashion_id: str, lottery_card_image: str, item_name: str, dt_imitation_rows_data: dict) -> None:
    base_output_dir = Path(__file__).resolve().parent.parent / 'dist'

    lottery_card_image_path = resolve_resource_path(lottery_card_image, '.png')

    if not lottery_card_image_path or not os.path.isfile(lottery_card_image_path):
        print(f"抽卡图片文件不存在: {lottery_card_image_path}")
    else:
        # 从 Hotta 开始的相对路径
        parts = Path(lottery_card_image_path).parts
        try:
            hotta_index = parts.index("Hotta")
            relative_dir = Path(*parts[hotta_index:-1])  # 不要最后一个文件名
            original_ext = Path(lottery_card_image_path).suffix
            target_path = base_output_dir / relative_dir / f"{item_name}{original_ext}"

            target_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(lottery_card_image_path, target_path)
        except ValueError:
            print(f"无法识别 Hotta 路径: {lottery_card_image_path}")

    if weapon_fashion_id == 'None':
        return
    else:
        name_picture_path = resolve_resource_path(dt_imitation_rows_data[weapon_fashion_id]['Name3Picture']['AssetPathName'],'.png')
        if not name_picture_path or not os.path.isfile(name_picture_path):
            print(f"抽卡名称文件不存在: {name_picture_path}")
        else:
            parts = Path(name_picture_path).parts
            try:
                hotta_index = parts.index("Hotta")
                relative_dir = Path(*parts[hotta_index:-1])
                original_ext = Path(name_picture_path).suffix
                target_path = base_output_dir / relative_dir / f"{item_name}{original_ext}"

                target_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(name_picture_path, target_path)
            except ValueError:
                print(f"无法识别 Hotta 路径: {name_picture_path}")
