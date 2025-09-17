import asyncio
import os

import httpx
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from playwright.async_api import async_playwright

from utils.font_server import FontServer
from utils.screenshots_utils import make_fonts_url, \
    make_recipes_background_url, com_lbl_green, highlight_shuzhi

from dotenv import load_dotenv
from asyncio import Semaphore

# 加载 .env 文件
load_dotenv()

# 原数据目录

x_api_key = os.getenv("X_API_KEY")
api_url = os.getenv("API_URL")

# 控制最多同时打开多少个页面
MAX_CONCURRENT_PAGES = 4


async def process_food(food: dict, env: Environment, browser, screenshot_dir: Path, semaphore: Semaphore,
                       font_server_port: int):
    async with semaphore:
        food = make_fonts_url(food, font_server_port)

        make_recipes_background_url(food)

        parts = []
        if food.get("useDescription"):
            parts.append(food["useDescription"])
        if food.get("buffs"):
            parts.append(food["buffs"])

        food["effect"] = "<br>".join(parts)

        template = env.get_template("template-food.html")
        html_content = template.render(**food)

        page = await browser.new_page()
        await page.set_content(html_content, timeout=600000)

        locator = page.locator(".card")
        screenshot_path = screenshot_dir / f"{food['foodName']}.png"
        await locator.screenshot(path=str(screenshot_path))
        await page.close()


async def make_all_food_image():
    font_server_port = 2288
    font_dir = Path(__file__).parent.parent.parent / "assets" / "fonts"
    server = FontServer(str(font_dir), port=font_server_port)
    server.start()

    try:

        screenshot_dir = Path(__file__).parent.parent.parent / "dist" / "screenshots" / "recipes"
        screenshot_dir.mkdir(exist_ok=True)
        files = [file.stem for file in screenshot_dir.iterdir() if file.is_file()]

        headers = {
            "Content-Type": "application/json",
            "X-API-KEY": x_api_key,
        }

        response = httpx.get(f'{api_url}/food', headers=headers)

        data = response.json()

        food_list = data['data']

        food_list = [w for w in food_list if w["foodName"] not in files]

        template_dir = Path(__file__).parent.parent.parent / "templates"
        env = Environment(loader=FileSystemLoader(str(template_dir)))

        env.filters['com_lbl_green'] = com_lbl_green
        env.filters['highlight_shuzhi'] = highlight_shuzhi

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            semaphore = Semaphore(MAX_CONCURRENT_PAGES)

            tasks = [
                process_food(food, env, browser, screenshot_dir, semaphore, font_server_port)
                for food in food_list
            ]
            await asyncio.gather(*tasks)

            await browser.close()
    finally:
        server.stop()


if __name__ == "__main__":
    asyncio.run(make_all_food_image())
