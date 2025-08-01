import asyncio
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from playwright.async_api import async_playwright

from models import Weapons, WeaponUpgradeStarPack, WeaponSensualityLevelData, WeaponSkill
from utils.font_server import FontServer
from utils.screenshots_utils import make_fonts_url, make_minio_img_url, make_item_name_icon, weapons_num_to_desc, \
    make_weapons_background_url, highlight_shuzhi
from tortoise import Tortoise

from config import database_config
from asyncio import Semaphore



# 控制最多同时打开多少个页面
MAX_CONCURRENT_PAGES = 4

async def make_weapons_skill_page(weapons: dict, font_server_port: int, env: Environment, page_sema: Semaphore, screenshot_dir: Path, browser):
    async with page_sema:
        # 字段处理
        weapons = make_fonts_url(weapons, font_server_port)
        weapons['item_icon'] = make_minio_img_url(weapons['item_icon'])
        weapons['weapon_category'] = make_item_name_icon(weapons['weapon_category'])
        weapons['weapon_element_type'] = make_item_name_icon(weapons['weapon_element_type'])
        weapons['armor_broken'] = weapons_num_to_desc(weapons['armor_broken'])
        weapons['charging'] = weapons_num_to_desc(weapons['charging'])
        make_weapons_background_url(weapons)

        # 获取技能数据
        weapon_skill = await WeaponSkill.filter(weapons_id=weapons["weapons_id"]).values("skill_type", "item_name", "item_describe")

        def get_type(skills, skill_type):
            return [s for s in skills if s["skill_type"] == skill_type] or None

        weapons["weapon_melee"] = get_type(weapon_skill, "普攻")
        weapons["weapon_back_attack"] = get_type(weapon_skill, "闪避")
        weapons["weapon_skill_attack"] = get_type(weapon_skill, "技能")
        weapons["weapon_success"] = get_type(weapon_skill, "联携")

        # 渲染 HTML
        template = env.get_template("template-weapons-skill.html")
        html_content = template.render(**weapons)

        # 创建页面并截图
        page = await browser.new_page()
        await page.set_content(html_content, timeout=600000)
        locator = page.locator(".card")
        screenshot_path = screenshot_dir / f"{weapons['item_name']}.png"
        await locator.screenshot(path=str(screenshot_path))
        await page.close()


async def make_all_weapons_skill_image():
    font_server_port = 2288
    font_dir = Path(__file__).parent.parent / "assets" / "fonts"
    server = FontServer(str(font_dir), port=font_server_port)
    server.start()

    try:
        # 初始化数据库
        await Tortoise.init(config=database_config.TORTOISE_ORM)

        screenshot_dir = Path(__file__).parent.parent / "dist" / "screenshots" / "weapons-skill"
        screenshot_dir.mkdir(exist_ok=True)

        files = {file.stem for file in screenshot_dir.iterdir() if file.is_file()}

        weapons_list = await Weapons.all().values(
            "weapons_id", "item_name", "item_rarity", "weapon_category",
            "weapon_element_type", "weapon_element_name", "weapon_element_desc",
            "armor_broken", "charging", "item_icon", "description", "remould_detail"
        )

        weapons_list = [w for w in weapons_list if w["item_name"] not in files]

        # Jinja2 环境
        template_dir = Path(__file__).parent.parent / "templates"
        env = Environment(loader=FileSystemLoader(str(template_dir)))
        env.filters['highlight_shuzhi'] = highlight_shuzhi

        # 开始浏览器
        async with async_playwright() as p:
            browser = await p.firefox.launch(headless=True)
            semaphore = Semaphore(MAX_CONCURRENT_PAGES)  # 最多 4 个并发任务
            tasks = [
                make_weapons_skill_page(w, font_server_port, env, semaphore, screenshot_dir, browser)
                for w in weapons_list
            ]
            await asyncio.gather(*tasks)
            await browser.close()

    finally:
        server.stop()



if __name__ == "__main__":
    asyncio.run(make_all_weapons_skill_image())
