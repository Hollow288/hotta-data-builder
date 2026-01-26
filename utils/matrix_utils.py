import json

from utils.common_utils import extract_tail_name, format_description, resolve_resource_path, fix_resolve_resource_path


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
                                     game_json: dict) -> list:
    """
    单纯用于意志套装效果整理

    """

    result_suit_unactivate_detail = []

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
            tem = {}
            tem['type'] = '意志3件装备效果'
            tem['desc'] = format_description(item_des, value_list)
            result_suit_unactivate_detail.append(tem)

        else:
            tem = {}
            tem['type'] = f'意志{num}件装备效果'
            tem['desc'] = format_description(item_des, value_list)
            result_suit_unactivate_detail.append(tem)
    return result_suit_unactivate_detail


def make_suit_list(
    static_matrix_data_rows_data: dict,
    name: str,
    matrix_upgrade_star_data_rows_data: dict,
    matrix_strengthen_data_rows_data: dict,
    equip_strengthen_effect_pack_rows_data: dict,
    modify_data_table_rows_data: dict,
    game_json: dict,
    attribute_static_data: dict
) -> list:
    name_lower = name.lower()

    suit_list = [
        val
        for val in static_matrix_data_rows_data.values()
        if "SuitID" in val and val["SuitID"].lower() == name_lower
    ]

    result_list = []

    for suit in suit_list:
        strengthen_pack_id = suit.get("StrengthenPackID")
        if not strengthen_pack_id:
            continue

        prefix = f"{strengthen_pack_id}_"

        temp_strengthen_dict = {
            key: val
            for key, val in matrix_strengthen_data_rows_data.items()
            if key.startswith(prefix)
        }

        add_attr_values_list = []

        for strengthen_val in temp_strengthen_dict.values():
            modify_pack_id = strengthen_val.get("ModifyPack")
            if not modify_pack_id:
                continue

            effect_pack = equip_strengthen_effect_pack_rows_data.get(modify_pack_id)
            if not effect_pack:
                continue

            add_attr_values = effect_pack.get("AddAttrValues")
            if add_attr_values:
                add_attr_values_list.append(add_attr_values)

        modify_data_key = suit.get("ModifyData")
        if not modify_data_key:
            continue

        raw_modify_list = (
            modify_data_table_rows_data
            .get(modify_data_key.lower(), {})
            .get("ModifyData", [])
        )

        source_modify = []

        for item in raw_modify_list:

            source_modify.append({
                "propName": item.get("PropName"),
                "propChsName": game_json["QRSLCommon_ST"].get(item["PropName"], item["PropName"]),
                "propValue": item.get("PropValue"),
                "modifierOp": item.get("ModifierOp"),
                "attributeIcon": fix_resolve_resource_path(attribute_static_data[item["PropName"]]['AttributeIcon']['AssetPathName'], '.webp'),
            })


        upgrade_star_pack_id = suit.get("UpgradeStarPackID")
        max_star_level = suit.get("MaxStarLevel", 0)

        matrix_coefficient_list = []

        if upgrade_star_pack_id and max_star_level:
            for star in range(0, max_star_level + 1):
                key = f"{upgrade_star_pack_id}_{star}"
                star_data = matrix_upgrade_star_data_rows_data.get(key)
                if not star_data:
                    continue

                coefficient = star_data.get("Coefficient")
                if coefficient is not None:
                    matrix_coefficient_list.append(coefficient)

        type_map = {
            "WEAPON_MATRIX_SLOT_FIRST": "mind",
            "WEAPON_MATRIX_SLOT_SECOND": "memory",
            "WEAPON_MATRIX_SLOT_THIRD": "belief",
            "WEAPON_MATRIX_SLOT_FOURTH": "emotion"
        }

        result_list.append({
            "itemName":game_json.get(extract_tail_name(suit['ItemName']['TableId']), {}).get(
                suit['ItemName']['Key'],
                suit['ItemName'].get('LocalizedString')
            ),
            "slotIndex": suit.get("SlotIndex"),
            "type": type_map.get(suit.get("SlotIndex")),
            "matrixMaxStrengthenLevel": suit.get("BaseMaxStrengthenLevel"),
            "description": game_json.get(extract_tail_name(suit['Description']['TableId']), {}).get(
                suit['Description']['Key'],
                suit['Description'].get('LocalizedString')
            ),
            "matrixUpgradeAttribute": add_attr_values_list,
            "matrixModifyData": source_modify,
            "matrixCoefficientList": matrix_coefficient_list,

        })

    return result_list