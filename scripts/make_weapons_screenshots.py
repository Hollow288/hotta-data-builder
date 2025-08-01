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

async def make_all_weapons_image():
    font_server_port = 2288

    font_dir = Path(__file__).parent.parent / "assets" / "fonts"
    server = FontServer(str(font_dir), port=font_server_port)
    server.start()
    try:
        # 初始化数据库
        await Tortoise.init(
            config=database_config.TORTOISE_ORM
        )

        screenshot_dir = Path(__file__).parent.parent / "dist" / "screenshots" / "weapons"
        screenshot_dir.mkdir(exist_ok=True)

        files = [file.stem for file in screenshot_dir.iterdir() if file.is_file()]

        weapons_list = await Weapons.all().values("weapons_id","item_name", "item_rarity", "weapon_category",
                                                                 "weapon_element_type", "weapon_element_name",
                                                                 "weapon_element_desc", "armor_broken", "charging",
                                                                 "item_icon", "description", "remould_detail")

        weapons_list = [weapons for weapons in weapons_list if weapons["item_name"] not in files]

        # 创建 Jinja2 环境
        template_dir = Path(__file__).parent.parent / "templates"
        env = Environment(loader=FileSystemLoader(str(template_dir)))
        env.filters['highlight_shuzhi'] = highlight_shuzhi  # 注册过滤器

        async with async_playwright() as p:
            browser = await p.firefox.launch(headless=True)

            for weapons in weapons_list:
                weapons = make_fonts_url(weapons, font_server_port)
                weapons['item_icon'] = make_minio_img_url(weapons['item_icon'])
                weapons['weapon_category'] = make_item_name_icon(weapons['weapon_category'])
                weapons['weapon_element_type'] = make_item_name_icon(weapons['weapon_element_type'])
                weapons['armor_broken'] = weapons_num_to_desc(weapons['armor_broken'])
                weapons['charging'] = weapons_num_to_desc(weapons['charging'])

                make_weapons_background_url(weapons)

                # 星级
                weapon_upgrade_star_pack = await WeaponUpgradeStarPack.filter(weapons_id=weapons["weapons_id"]).values(
                    "item_name", "item_describe")
                # 通感
                weapon_sensuality_level_data = await WeaponSensualityLevelData.filter(
                    weapons_id=weapons["weapons_id"]).values("item_name", "item_describe")

                weapons["weapon_upgrade_star_pack"] = weapon_upgrade_star_pack if len(
                    weapon_upgrade_star_pack) > 0 else None
                weapons["weapon_sensuality_level_data"] = weapon_sensuality_level_data if len(
                    weapon_sensuality_level_data) > 0 else None

                # 渲染 HTML
                template = env.get_template("template-arms.html")
                html_content = template.render(**weapons)

                # 创建新的页面
                page = await browser.new_page()  # 每次处理新数据时创建新标签页

                # 加载 HTML 内容
                await page.set_content(html_content, timeout=600000)  # 60 秒

                # 截图特定区域 (定位到 .card)
                locator = page.locator(".card")

                screenshot_path = screenshot_dir / f"{weapons['item_name']}.png"
                await locator.screenshot(path=str(screenshot_path))

                # 关闭当前页面
                await page.close()

            await browser.close()

    finally:
        server.stop()




if __name__ == "__main__":
    asyncio.run(make_all_weapons_image())
