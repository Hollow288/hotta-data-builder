from utils.common_utils import fix_resolve_resource_path


def make_fashion_icons(art_pack_id: str, art_pack_data_table_rows_data: dict) -> list:
    art_info = art_pack_data_table_rows_data[art_pack_id]

    icons = art_info.get("Icons", [])

    filtered_icons = [icon for icon in icons if icon.get("AssetPathName") != "None"]

    result = [fix_resolve_resource_path(icon["AssetPathName"],".png") for icon in filtered_icons]

    return result