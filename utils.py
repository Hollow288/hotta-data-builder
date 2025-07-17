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
