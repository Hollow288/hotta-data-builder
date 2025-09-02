import json
import os

from dotenv import load_dotenv

from utils.artifact_utils import make_artifact_attribute_data, make_use_description
from utils.common_utils import extract_tail_name, fix_resolve_resource_path
from utils.weapons_utils import translate_weapon_info

# 加载 .env 文件
load_dotenv()

# 原数据目录
source_path = os.getenv("SOURCE_PATH")

artifact_data_table_path = os.getenv("ARTIFACT_DATA_TABLE") or os.path.join(
    source_path, "CoreBlueprints/DataTable/Artifact/ArtifactDataTable.json"
)

artifact_advance_attribute_data_table_path = os.getenv("ARTIFACT_ADVANCE_ATTRIBUTE_DATA_TABLE") or os.path.join(
    source_path, "CoreBlueprints/DataTable/Artifact/ArtifactAdvanceAttributeDataTable.json"
)


gameplay_ability_tips_data_table_path = os.getenv("GAMEPLAY_ABILITY_TIPS_DATA_TABLE") or os.path.join(
    source_path, "CoreBlueprints/DataTable/GameplayAbilityTipsDataTable.json"
)


skill_update_tips_path = os.getenv("SKILL_UPDATE_TIPS") or os.path.join(
    source_path, "CoreBlueprints/DataTable/Skill/SkillUpdateTips.json"
)


# Game.json文件目录
game_json_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "dist/intermediate", "Game.json"))


async def make_artifact_data():
    with open(artifact_data_table_path, "r", encoding="utf-8") as f:
        artifact_data_table = json.load(f)

    with open(artifact_advance_attribute_data_table_path, "r", encoding="utf-8") as f:
        artifact_advance_attribute_data_table = json.load(f)

    with open(gameplay_ability_tips_data_table_path, "r", encoding="utf-8") as f:
        gameplay_ability_tips_data = json.load(f)

    with open(skill_update_tips_path, "r", encoding="utf-8") as f:
        skill_update_tips = json.load(f)

    with open(game_json_path, "r", encoding="utf-8") as f:
        game_json = json.load(f)

    artifact_data_table_rows_data = artifact_data_table[0].get("Rows", {})

    artifact_advance_attribute_rows_data = artifact_advance_attribute_data_table[0].get("Rows", {})

    gameplay_ability_tips_data_rows_data = gameplay_ability_tips_data[0].get("Rows", {})

    skill_update_tips_rows_data = skill_update_tips[0].get("Rows", {})

    artifact_filter_data = {
        name: data
        for name, data in artifact_data_table_rows_data.items()
        if data.get("bCanExhibit") == True and data.get("ItemType") == 'ITEM_TYPE_ARTIFACT' and data.get(
            "bShowInIllustration") == True
    }

    output_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "dist/intermediate", "artifact_filter_data.json"))

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(artifact_filter_data, f, ensure_ascii=False, indent=2)

    result_artifact_dict = {}

    for name, data in artifact_filter_data.items():
        artifact_info = {
            "artifact_key": name,
            "item_name": game_json[extract_tail_name(data['ItemName']['TableId'])][data['ItemName']['Key']],
            "use_description": make_use_description(data['InitialSkill']['SkillTemplate']['AssetPathName'],gameplay_ability_tips_data_rows_data,skill_update_tips_rows_data,game_json),
            "item_rarity": translate_weapon_info(data['ItemRarity']),
            "card_image": fix_resolve_resource_path(data['CardImage']['AssetPathName'], '.png'),
            "artifact_attribute_data": make_artifact_attribute_data(data['AdvanceAttributeID'],artifact_advance_attribute_rows_data,game_json)
        }

        result_artifact_dict[name] = artifact_info

    output_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "dist/final", "artifact_data.json"))

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result_artifact_dict, f, ensure_ascii=False, indent=2)
