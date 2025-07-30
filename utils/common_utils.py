import os
import json
from pathlib import Path
from typing import List, Union, Dict, Any
from dotenv import load_dotenv
from typing import Any, Dict, Optional
import re


def extract_tail_name(path: str) -> str:
    """
    将原始路径中的文件名处理出来，用于从Game.json中找数据

    参数：
        path: 原始路径 例如：/Game/Resources/CoreBlueprints/DataTable/Skill/WeaponDes/LyncisDes.LyncisDes
    返回：
        文件名 也就是Game.json中的key
    """

    path = path.rstrip("/")

    last_part = path.split("/")[-1]

    if "." in last_part:
        return last_part.rsplit(".", 1)[0]

    return last_part


def resolve_resource_path(resource_string: str, ext: str = ".json") -> str:
    """
    将原始资源路径转换为相对于 SOURCE_PATH 的完整路径，并加上指定后缀。

    参数：
        resource_string: 原始资源路径（例如 C:/Game/Resources/...）
        ext: 目标文件后缀（默认 .json）

    返回：
        拼接后的完整路径字符串
    """
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

    # 去掉已有扩展名（保留路径结构中间的点）
    relative_path = Path(relative_part).with_suffix("")

    # 拼接路径
    full_path = source_path / relative_path

    # 拼接后缀（允许传入 "" 表示不加后缀）
    if ext:
        if not ext.startswith("."):
            ext = "." + ext
        full_path = full_path.with_suffix(ext)

    return full_path.as_posix()


def format_description(
        template: str,
        values: list[float],
        start_index: int = 0  # 新增参数，默认为0（保持原行为）
) -> str:
    """
    将存在数值占位符的描述，通过原文本+数值数组组合

    参数：
        template: 原文本
        values: 数值数组
        start_index：从数组的第几个索引开始

    返回：
        拼接后的完整描述

    """

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


def make_remould_detail(parms_some_base_info: dict, parms_game_json: dict):
    """
    对于一种常见数据格式的处理RemouldDetail存描述，RemouldDetailParams存数值，并且数值在单独文件中的
    """

    if parms_some_base_info.get('RemouldDetail', {}).get('Key'):
        source_string = parms_game_json[extract_tail_name(parms_some_base_info['RemouldDetail']['TableId'])][
            parms_some_base_info['RemouldDetail']['Key']]

        # 处理数值部分
        remould_detail_params_list = parms_some_base_info['RemouldDetailParams']

        result_remould_numeric_list = []

        for remould_detail_params in remould_detail_params_list:

            if remould_detail_params['Curve']['RowName'] == 'None':
                continue

            resolve_path = resolve_resource_path(remould_detail_params['Curve']['CurveTable']['ObjectPath'])
            with open(resolve_path, "r", encoding="utf-8") as nj:
                numeric_json = json.load(nj)

            numeric_key_val = numeric_json[0].get("Rows", {})

            result_remould_numeric_list.append(
                numeric_key_val[remould_detail_params['Curve']['RowName']]['Keys'][0]['Value'] * remould_detail_params[
                    'Value'])

        return format_description(source_string, result_remould_numeric_list)
    else:
        return None


def find_parent_value_by_key_value(
        data: Dict[str, Any],
        target_key: str,
        target_value: Any,
        max_depth: int = 0
) -> Optional[Dict[str, Any]]:
    """
    在嵌套字典中查找第一个满足 key=value 的项（忽略大小写），
    返回该 key 所在的父级 dict（即兄弟字段）。

    参数:
        data (dict): 要搜索的嵌套字典
        target_key (str): 要查找的键（忽略大小写）
        target_value (Any): 要查找的值（忽略大小写）
        max_depth (int): 最大递归层级（0 表示只查顶层）

    返回:
        找到的那一层字典，或 None
    """

    def _normalize(val: Any) -> str:
        """将值转换为统一的小写字符串，用于大小写无关比较"""
        return str(val).lower()

    def _search(current: Any, current_depth: int) -> Optional[Dict[str, Any]]:
        if not isinstance(current, dict):
            return None

        if current_depth > max_depth:
            return None

        for k, v in current.items():
            # 如果 key 和 value 都匹配（忽略大小写）
            if _normalize(k) == _normalize(target_key) and _normalize(v) == _normalize(target_value):
                return current

        # 递归向下查找
        for value in current.values():
            result = _search(value, current_depth + 1)
            if result is not None:
                return result

        return None

    return _search(data, 0)
