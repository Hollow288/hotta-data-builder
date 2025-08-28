import json
import os

from dotenv import load_dotenv

from utils.common_utils import extract_tail_name
from utils.fashion_utils import make_fashion_icons

#加载 .env 文件
load_dotenv()

# 原数据目录
source_path = os.getenv("SOURCE_PATH")

fashion_data_table_path = os.getenv("FASHION_DATA_TABLE") or os.path.join(
    source_path, "CoreBlueprints/DataTable/Fashion/FashionDataTable.json"
)

art_pack_data_table_path = os.getenv("ART_PACK_DATA_TABLE") or os.path.join(
    source_path, "CoreBlueprints/DataTable/ArtPackDataTable.json"
)

# Game.json文件目录
game_json_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "dist/intermediate", "Game.json"))


async def make_fashion_data():

    with open(fashion_data_table_path, "r", encoding="utf-8") as f:
        fashion_data_table = json.load(f)

    with open(art_pack_data_table_path, "r", encoding="utf-8") as f:
        art_pack_data_table = json.load(f)

    with open(game_json_path, "r", encoding="utf-8") as f:
        game_json = json.load(f)

    fashion_data_table_rows_data = fashion_data_table[0].get("Rows", {})

    art_pack_data_table_rows_data = art_pack_data_table[0].get("Rows", {})

    fashion_filter_data = {
        name: data
        for name, data in fashion_data_table_rows_data.items()
        if data.get("FashionType") == "EFashionType::Dress" and data.get("ItemId") != "None"
    }

    output_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "dist/intermediate", "fashion_filter_data.json"))

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(fashion_filter_data, f, ensure_ascii=False, indent=2)

    result_fashion_dict = {}

    for name, data in fashion_filter_data.items():
        fashion_info = {
            "fashion_key": name,
            "fashion_Name": data['Name']['LocalizedString'],
            "Description": data['Description']['LocalizedString'],
            "ActiveSource": data.get('ActiveSource', {}).get('LocalizedString', ''),
            "Icons": make_fashion_icons(data['ArtPackID'],art_pack_data_table_rows_data)
        }

        result_fashion_dict[name] = fashion_info


    output_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "dist/final", "fashion_data.json"))

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result_fashion_dict, f, ensure_ascii=False, indent=2)