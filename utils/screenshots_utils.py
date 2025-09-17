import os
import re

from dotenv import load_dotenv

from pathlib import Path

load_dotenv()

ENDPOINT = os.getenv("ENDPOINT")

def make_fonts_url(font_map: dict, port: int) -> dict:
    font_dir = Path(__file__).parent.parent / "assets" / "fonts"
    base_url = f"http://localhost:{port}"

    for file in font_dir.iterdir():
        if file.is_file():
            original_stem = file.stem

            # 将非法字符替换成下划线，只保留字母、数字、下划线
            key = re.sub(r'\W|^(?=\d)', '_', original_stem)

            font_map[key] = f"{base_url}/{file.name}"

    return font_map


def make_minio_img_url(url: str) -> str:
    endpoint = os.getenv("ENDPOINT", "localhost:9000")
    return f"http://{endpoint}/hotta/{url}"


def make_item_name_icon(weapon_category: str) -> str:
    bucket_name = 'hotta-basic-icon'
    endpoint = os.getenv("ENDPOINT", "localhost:9000")

    item_name_dict = {
        '物理': 'icon_element_wu.webp',
        '火焰': 'icon_element_huo.webp',
        '寒冰': 'icon_element_bing.webp',
        '雷电': 'icon_element_lei.webp',
        '异能': 'icon_element_powers.webp',
        '物火': 'icon_element_wuhuo.webp',
        '火物': 'icon_element_huowu.webp',
        '冰雷': 'icon_element_binglei.webp',
        '雷冰': 'icon_element_leibing.webp',
        '强攻': 'icon_qianggong.webp',
        '坚毅': 'icon_fangyu.webp',
        '恩赐': 'icon_zengyi.webp'
    }

    return f"http://{endpoint}/{bucket_name}/{item_name_dict[weapon_category]}"



def weapons_num_to_desc(weapons_num: float) -> str:
    if weapons_num >= 14.1:
        return "SS"
    elif weapons_num >= 10.1:
        return "S"
    elif weapons_num >= 7:
        return "A"
    else:
        return "B"


def make_weapons_background_url(weapons:dict):
    bucket_name = 'hotta-weapons-background'

    endpoint = os.getenv("ENDPOINT", "localhost:9000")

    weapons['background_url'] = f"http://{endpoint}/{bucket_name}/background-{weapons['weaponName']}.jpeg"

    weapons['default_background_url'] = f"http://{endpoint}/{bucket_name}/background-arms.jpeg"

def make_matrix_background_url(weapons:dict):
    bucket_name = 'hotta-weapons-background'

    endpoint = os.getenv("ENDPOINT", "localhost:9000")

    weapons['default_background_url'] = f"http://{endpoint}/{bucket_name}/background-willpower.jpeg"


def highlight_shuzhi(value: str) -> str | None:
    return re.sub(r"<shuzhi>(.*?)</>", r'<span style="color:red">\1</span>', value)

def com_lbl_green(value: str) -> str | None:
    return re.sub(r"<ComLblGreen>(.*?)</>", r'<span style="color:green">\1</span>', value)


def make_recipes_background_url(recipes:dict):
    bucket_name = 'hotta-common-screenshots'

    endpoint = os.getenv("ENDPOINT", "localhost:9000")

    recipes['background_url'] = f"http://{endpoint}/{bucket_name}/background-food.webp"

    recipes['background_foliage'] = f"http://{endpoint}/{bucket_name}/background-foliage.jpg"











