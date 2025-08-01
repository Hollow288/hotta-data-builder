import asyncio
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from playwright.async_api import async_playwright

from models import Weapons, WeaponUpgradeStarPack, WeaponSensualityLevelData
from utils.font_server import FontServer
from utils.screenshots_utils import make_fonts_url, make_minio_img_url, make_item_name_icon, weapons_num_to_desc, \
    make_weapons_background_url, highlight_shuzhi
from tortoise import Tortoise

from config import database_config
from asyncio import Semaphore


# 控制最多同时打开多少个页面
MAX_CONCURRENT_PAGES = 4

async def process_weapon(weapons: dict, env: Environment, browser, screenshot_dir: Path, semaphore: Semaphore, font_server_port: int):
    async with semaphore:
        weapons = make_fonts_url(weapons, font_server_port)
        weapons['item_icon'] = make_minio_img_url(weapons['item_icon'])
        weapons['weapon_category'] = make_item_name_icon(weapons['weapon_category'])
        weapons['weapon_element_type'] = make_item_name_icon(weapons['weapon_element_type'])
        weapons['armor_broken'] = weapons_num_to_desc(weapons['armor_broken'])
        weapons['charging'] = weapons_num_to_desc(weapons['charging'])

        make_weapons_background_url(weapons)

        weapon_upgrade_star_pack = await WeaponUpgradeStarPack.filter(
            weapons_id=weapons["weapons_id"]).values("item_name", "item_describe")
        weapon_sensuality_level_data = await WeaponSensualityLevelData.filter(
            weapons_id=weapons["weapons_id"]).values("item_name", "item_describe")

        weapons["weapon_upgrade_star_pack"] = weapon_upgrade_star_pack or None
        weapons["weapon_sensuality_level_data"] = weapon_sensuality_level_data or None

        template = env.get_template("template-weapons.html")
        html_content = template.render(**weapons)

        page = await browser.new_page()
        await page.set_content(html_content, timeout=600000)

        locator = page.locator(".card")
        screenshot_path = screenshot_dir / f"{weapons['item_name']}.png"
        await locator.screenshot(path=str(screenshot_path))
        await page.close()

async def make_all_weapons_image():
    font_server_port = 2288
    font_dir = Path(__file__).parent.parent / "assets" / "fonts"
    server = FontServer(str(font_dir), port=font_server_port)
    server.start()

    try:
        await Tortoise.init(config=database_config.TORTOISE_ORM)

        screenshot_dir = Path(__file__).parent.parent / "dist" / "screenshots" / "weapons"
        screenshot_dir.mkdir(exist_ok=True)
        files = [file.stem for file in screenshot_dir.iterdir() if file.is_file()]

        weapons_list = await Weapons.all().values("weapons_id", "item_name", "item_rarity", "weapon_category",
            "weapon_element_type", "weapon_element_name", "weapon_element_desc", "armor_broken", "charging",
            "item_icon", "description", "remould_detail")

        weapons_list = [w for w in weapons_list if w["item_name"] not in files]

        template_dir = Path(__file__).parent.parent / "templates"
        env = Environment(loader=FileSystemLoader(str(template_dir)))
        env.filters['highlight_shuzhi'] = highlight_shuzhi

        async with async_playwright() as p:
            browser = await p.firefox.launch(headless=True)
            semaphore = Semaphore(MAX_CONCURRENT_PAGES)

            tasks = [
                process_weapon(weapons, env, browser, screenshot_dir, semaphore, font_server_port)
                for weapons in weapons_list
            ]
            await asyncio.gather(*tasks)

            await browser.close()
    finally:
        server.stop()




if __name__ == "__main__":
    asyncio.run(make_all_weapons_image())
