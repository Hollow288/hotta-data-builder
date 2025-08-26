import os
import json
from pathlib import Path
from typing import List, Union, Dict, Any
from dotenv import load_dotenv
from typing import Any, Dict, Optional

# 加载 .env 配置
load_dotenv()

# 从 .env 获取源数据根目录
source_path = os.getenv("SOURCE_PATH")  # 例：C:/XM/MY/Hotta/Content/Resources

# 拼接成完整路径列表
paths = [
    os.path.join(source_path, "CoreBlueprints/DataTable/Skill"),
    os.path.join(source_path, "Text/ST_item.json"),
    os.path.join(source_path, "Text/ST_Equipment.json"),
    os.path.join(source_path, "Text/QRSLCommon_ST.json"),
    os.path.join(source_path, "Text/UI.json")
]


def find_keys_to_entries(data: Any) -> Dict[str, Any]:
    """
    递归查找 JSON 中所有 KeysToEntries 字段并合并 传入的是路径列表  （构成Game.json使用）
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


async def generate_game_json():
    # 加载数据
    grouped_data = load_keys_to_entries_grouped(paths)

    # 构建输出路径
    output_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "dist", "intermediate", "Game.json"))
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(grouped_data, f, ensure_ascii=False, indent=2)
    print(f"✅ 生成完成: {output_path}")
