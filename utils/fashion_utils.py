from utils.common_utils import fix_resolve_resource_path


def make_fashion_icons(art_pack_id: str, art_pack_data_table_rows_data: dict, base_icon: str) -> list:
    art_info = art_pack_data_table_rows_data[art_pack_id]

    icons = art_info.get("Icons", [])

    filtered_icons = [icon for icon in icons if icon.get("AssetPathName") != "None" and icon.get("AssetPathName") != base_icon]

    result = [fix_resolve_resource_path(icon["AssetPathName"],".webp") for icon in filtered_icons]

    return result