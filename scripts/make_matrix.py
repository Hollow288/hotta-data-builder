import os
import shutil
from pathlib import Path

from dotenv import load_dotenv
import json

from utils.common_utils import extract_tail_name, find_parent_value_by_key_value, resolve_resource_path
from utils.matrix_utils import translate_matrix_info, make_suit_unactivate_detail_list

# 加载 .env 文件
load_dotenv()

# 原数据目录
source_path = os.getenv("SOURCE_PATH")

# 意志列表起点文件目录
static_matrix_suit_data_table_path = os.getenv("STATIC_MATRIX_SUIT_DATA_TABLE") or os.path.join(
    source_path, "CoreBlueprints/DataTable/WeaponData/WeaponMatrix/StaticMatrixSuitDataTable.json"
)

static_matrix_data_path = os.getenv("STATIC_MATRIX_DATA") or os.path.join(
    source_path, "CoreBlueprints/DataTable/WeaponData/WeaponMatrix/StaticMatrixData.json"
)

# Game.json文件目录
game_json_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "dist/intermediate", "Game.json"))

if __name__ == "__main__":
    with open(static_matrix_suit_data_table_path, "r", encoding="utf-8") as f:
        static_matrix_suit_data_table = json.load(f)

    with open(static_matrix_data_path, "r", encoding="utf-8") as f:
        static_matrix_data = json.load(f)

    with open(game_json_path, "r", encoding="utf-8") as f:
        game_json = json.load(f)

    static_matrix_suit_data_table_rows_data = static_matrix_suit_data_table[0].get("Rows", {})

    static_matrix_data_rows_data = static_matrix_data[0].get("Rows", {})

    output_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "dist/intermediate", "matrix_filtered.json"))
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(static_matrix_suit_data_table_rows_data, f, ensure_ascii=False, indent=2)

    result_matrix_dict = {}

    for name, data in static_matrix_suit_data_table_rows_data.items():
        matrix_info = {
            'SuitName': game_json[extract_tail_name(data['SuitName']['TableId'])][data['SuitName']['Key']],
            'MatrixSuitQuality': translate_matrix_info(data['MatrixSuitQuality']),
            'SuitIcon': resolve_resource_path(
                find_parent_value_by_key_value(static_matrix_data_rows_data, 'SuitID', name, 1)['ItemLargeIcon'][
                    'AssetPathName'], '.png'),
            "SuitUnactivateDetailList": make_suit_unactivate_detail_list(data['SuitUnactivateDetailList'],
                                                                         data['SuitUnactivateDetailParams'],
                                                                         data['MatrixSuitQuality'], game_json)
        }

        result_matrix_dict[name] = matrix_info

    # 最终保存
    output_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "dist/final", "matrix.json"))
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result_matrix_dict, f, ensure_ascii=False, indent=2)

    base_output_dir = Path(__file__).resolve().parent.parent / 'dist'

    for key, item in result_matrix_dict.items():
        icon_path = item.get("SuitIcon")
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
