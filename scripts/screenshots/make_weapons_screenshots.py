import asyncio
import os
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from playwright.async_api import async_playwright
import httpx
from utils.font_server import FontServer
from utils.screenshots_utils import make_fonts_url, make_minio_img_url, make_item_name_icon, weapons_num_to_desc, \
    make_weapons_background_url, highlight_shuzhi
from dotenv import load_dotenv
from asyncio import Semaphore

# 加载 .env 文件
load_dotenv()

# 原数据目录

x_api_key = os.getenv("X_API_KEY")
api_url = os.getenv("API_URL")

# 控制最多同时打开多少个页面
MAX_CONCURRENT_PAGES = 4


async def process_weapon(weapons: dict, env: Environment, browser, screenshot_dir: Path, semaphore: Semaphore,
                         font_server_port: int):
    async with semaphore:
        weapons = make_fonts_url(weapons, font_server_port)
        weapons['weaponCategory'] = make_item_name_icon(weapons['weaponCategory'])
        weapons['weaponElementType'] = make_item_name_icon(weapons['weaponElement']['weaponElementType'])
        weapons['armorBroken'] = weapons_num_to_desc(weapons['armorBroken'])
        weapons['charging'] = weapons_num_to_desc(weapons['charging'])

        make_weapons_background_url(weapons)

        template = env.get_template("template-weapons.html")
        html_content = template.render(**weapons)

        page = await browser.new_page()
        await page.set_content(html_content, timeout=600000)

        locator = page.locator(".card")
        screenshot_path = screenshot_dir / f"{weapons['weaponName']}.png"
        await locator.screenshot(path=str(screenshot_path))
        await page.close()


async def make_all_weapons_image():
    font_server_port = 2288
    font_dir = Path(__file__).parent.parent.parent / "assets" / "fonts"
    server = FontServer(str(font_dir), port=font_server_port)
    server.start()

    try:
        screenshot_dir = Path(__file__).parent.parent.parent / "dist" / "screenshots" / "weapons"
        screenshot_dir.mkdir(exist_ok=True)
        files = [file.stem for file in screenshot_dir.iterdir() if file.is_file()]

        headers = {
            "Content-Type": "application/json",
            "X-API-KEY": x_api_key,
        }

        response = httpx.get(f'{api_url}/weapons', headers=headers)

        data = response.json()

        weapons_list = data['data']

        weapons_list = [w for w in weapons_list if w["weaponName"] not in files]

        template_dir = Path(__file__).parent.parent.parent / "templates"
        env = Environment(loader=FileSystemLoader(str(template_dir)))
        env.filters['highlight_shuzhi'] = highlight_shuzhi

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
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
