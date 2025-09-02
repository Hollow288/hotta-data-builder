from utils.common_utils import extract_tail_name, format_description
from utils.weapons_utils import make_weapon_skill_desc_value


def make_use_description(asset_path_name: str, gameplay_ability_tips_data_rows_data: dict,
                         skill_update_tips_rows_data: dict,game_json:dict) -> str:
    item = gameplay_ability_tips_data_rows_data[extract_tail_name(asset_path_name)]

    item_desc_tem = game_json[extract_tail_name(item['Desc']['TableId'])][item['Desc']['Key']]

    values = make_weapon_skill_desc_value(item['GAParamName'], item['GAParameNum'],
                                          skill_update_tips_rows_data)

    item_desc = format_description(item_desc_tem, values)

    return item_desc






def make_artifact_attribute_data(attribute_id: str, artifact_advance_attribute_rows_data: dict,
                                 game_json: dict) -> list:
    attribute_data = {
        name: data
        for name, data in artifact_advance_attribute_rows_data.items()
        if data.get("AttributeID") == attribute_id
    }

    sorted_items = sorted(attribute_data.values(), key=lambda x: x.get("CardStar", 0))

    results = []

    for item in sorted_items:
        results.append(game_json[extract_tail_name(item['Desc']['TableId'])][item['Desc']['Key']].strip())

    return results
