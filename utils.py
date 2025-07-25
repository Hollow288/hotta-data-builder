import os
import json
from pathlib import Path
from typing import List, Union, Dict, Any
from dotenv import load_dotenv

def find_keys_to_entries(data: Any) -> Dict[str, Any]:
    """
    递归查找 JSON 中所有 KeysToEntries 字段并合并
    """
    result = {}

    if isinstance(data, dict):
        for key, value in data.items():
            if key == "KeysToEntries" and isinstance(value, dict):
                result.update(value)
            else:
                result.update(find_keys_to_entries(value))
    elif isinstance(data, list):
        for item in data:
            result.update(find_keys_to_entries(item))

    return result


def generate_unique_key(base_name: str, existing_keys: set) -> str:
    """
    为文件名生成唯一 key，避免重复（如 weapon_a、weapon_a#1、weapon_a#2）
    如果有重复，会在控制台提示。
    """
    if base_name not in existing_keys:
        return base_name

    print(f"[提示] 检测到重复的 key: '{base_name}'，自动重命名以避免冲突...")

    i = 1
    while f"{base_name}#{i}" in existing_keys:
        i += 1
    new_key = f"{base_name}#{i}"
    print(f"[提示] 新 key 分配为: '{new_key}'")
    return new_key


def load_keys_to_entries_grouped(paths: List[Union[str, Path]]) -> Dict[str, Dict[str, Any]]:
    """
    读取多个 json 文件中的 KeysToEntries 字段，使用无后缀文件名为 key，
    避免重复命名时添加编号后缀。
    """
    result = {}
    seen_keys = set()

    for path in paths:
        path = Path(path)
        if path.is_file() and path.suffix == ".json":
            _add_file(result, seen_keys, path)
        elif path.is_dir():
            for file in path.rglob("*.json"):
                _add_file(result, seen_keys, file)
        else:
            print(f"⚠️ 无效路径：{path}")

    return result


def _add_file(result: Dict, seen_keys: set, file_path: Path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = json.load(f)
            entries = find_keys_to_entries(content)
            if not entries:
                return

            # 去掉后缀得到基础名（如 weapon_a）
            base_name = file_path.stem
            key = generate_unique_key(base_name, seen_keys)
            seen_keys.add(key)

            result[key] = entries

    except Exception as e:
        print(f"❌ 无法解析 {file_path}: {e}")


def extract_tail_name(path: str) -> str:
    """
    提取路径中的最后名字：
    - 如果有 '.'，返回最后一个 '.' 后的部分
    - 如果没有 '.'，返回最后一个 '/' 后的部分
    """
    if "." in path:
        return path.split(".")[-1]
    return path.rstrip("/").split("/")[-1]


def translate_weapon_info(key: str, element_type: int = 0) -> str:
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


def resolve_resource_path(resource_string: str) -> str:
    load_dotenv()
    source_path_str = os.getenv("SOURCE_PATH")
    if not source_path_str:
        raise ValueError("环境变量 SOURCE_PATH 未定义")

    source_path = Path(source_path_str.replace("\\", "/"))
    resource_string = resource_string.strip("\"").replace("\\", "/")

    # 获取 SOURCE_PATH 的最后一级目录名（不区分大小写）
    source_last_part = source_path.parts[-1].lower()

    # 在 resource_string 中找最后一级目录名的位置
    idx = resource_string.lower().find(source_last_part)
    if idx == -1:
        raise ValueError(f"resource_string 中未能匹配到 SOURCE_PATH 的最后一级目录 '{source_last_part}'")

    # 获取匹配点之后的部分作为相对路径
    relative_part = resource_string[idx + len(source_last_part):].lstrip("/")

    # 处理可能的 .0 这样的后缀
    if "." in relative_part:
        relative_part = relative_part.split(".")[0]

    # 拼接路径
    full_path = source_path / relative_part

    # 确保添加 .json 后缀
    full_path = full_path.with_suffix(".json")

    return str(full_path)


import re

def format_description(
    template: str,
    values: list[float],
    start_index: int = 0  # 新增参数，默认为0（保持原行为）
) -> str:
    def format_number(n):
        n = float(n)
        if n.is_integer():
            return f"{int(n):,}"
        else:
            return f"{n:,.2f}".rstrip("0").rstrip(".")

    def replacer(match):
        placeholder_index = int(match.group(1))  # 占位符中的索引
        adjusted_index = placeholder_index - start_index  # 计算实际数据索引
        if 0 <= adjusted_index < len(values):
            return format_number(values[adjusted_index])
        return match.group(0)  # 越界保留原样

    return re.sub(r"\{(\d+)\}", replacer, template)



def extract_series_values(data: dict, base_key: str, game_json :dict) -> list:
    """
    提取以 base_key 为前缀、序号结尾（如 'sense_1', 'sense_2', ...）的字典值，直到找不到为止。

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



def make_element_desc_name(item_rarity: str, weapon_element_type: str, weapon_accessory_element_type: int, quip_batch_level_static_data_table_rows_data: dict, game_json: dict) -> dict:
    if weapon_accessory_element_type != 2 and  weapon_accessory_element_type != 0:
        print(weapon_accessory_element_type)

    if weapon_accessory_element_type == 2:
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

    if weapon_accessory_element_type == 0:
        name_fragment = {
            "EWeaponElementType::Superpower": "32",
            "EWeaponElementType::Physics": "2",
            "EWeaponElementType::Thunder": "16",
            "EWeaponElementType::Flame": "4",
            "EWeaponElementType::Ice": "8"
        }

        quip_batch_find = {
            "EWeaponElementType::Superpower": None,
            "EWeaponElementType::Physics": "Physics",
            "EWeaponElementType::Thunder": "Thunder",
            "EWeaponElementType::Flame": "fire",
            "EWeaponElementType::Ice": "Ice"
        }

    item_rarity_eff_name = {
        "EItemRarity::ITEM_RARITY_SSR": "2",
        "EItemRarity::ITEM_RARITY_SR": "1",
        "EItemRarity::ITEM_RARITY_R": "0",
    }

    template =  game_json['QRSLCommon_ST']["ui_weapon_charge_" + name_fragment[weapon_element_type] + "_desc_0"]

    if weapon_element_type == 'EWeaponElementType::Superpower':
        quip_batch_values = []
    else:
        quip_batch_dict = quip_batch_level_static_data_table_rows_data[quip_batch_find[weapon_element_type] + '_' + item_rarity_eff_name[item_rarity]]

        quip_batch_values = quip_batch_dict['GrowUpData'][0]['ParamValues']

    element_desc = format_description(template,quip_batch_values,1)

    element_name = game_json['QRSLCommon_ST']['ui_weapon_charge_' + name_fragment[weapon_element_type] + '_0']

    return {"element_desc" : element_desc, "element_name" : element_name}


