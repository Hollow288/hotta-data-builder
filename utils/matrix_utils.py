import json

from utils.common_utils import extract_tail_name, format_description, resolve_resource_path


def translate_matrix_info(key: str) -> str:
    """
    翻译意志品质
    """

    rarity_map = {
        "ITEM_QUALITY_COMMON": "N",
        "ITEM_QUALITY_RARE": "R",
        "ITEM_QUALITY_EPIC": "SR",
        "ITEM_QUALITY_LEGENDRY": "SSR"

    }

    return rarity_map.get(key, "Unknown")


def make_suit_unactivate_detail_list(detail_list: list, detail_params_list: list, matrix_suit_quality: str,
                                     game_json: dict) -> dict:
    """
    单纯用于意志套装效果整理

    """

    result_suit_unactivate_detail = {}

    for index, item in enumerate(detail_list):

        num = index * 2 + 2

        item_des = game_json[extract_tail_name(item['TableId'])][item['Key']]

        value_list = []

        if index < len(detail_params_list):

            params_list = detail_params_list[index]['ScalableFloatParams']

            for remould_detail_params in params_list:

                if remould_detail_params['Curve']['RowName'] == 'None':
                    continue

                resolve_path = resolve_resource_path(remould_detail_params['Curve']['CurveTable']['ObjectPath'])
                with open(resolve_path, "r", encoding="utf-8") as nj:
                    numeric_json = json.load(nj)

                numeric_key_val = numeric_json[0].get("Rows", {})

                value_list.append(
                    numeric_key_val[remould_detail_params['Curve']['RowName']]['Keys'][0]['Value'] *
                    remould_detail_params['Value'])

        if matrix_suit_quality != 'ITEM_QUALITY_LEGENDRY':
            result_suit_unactivate_detail['意志3件装备效果'] = format_description(item_des, value_list)
        else:
            result_suit_unactivate_detail[f'意志{num}件装备效果'] = format_description(item_des, value_list)

    return result_suit_unactivate_detail
