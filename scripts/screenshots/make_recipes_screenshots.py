import asyncio
import os
import httpx
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from playwright.async_api import async_playwright

from utils.font_server import FontServer
from utils.screenshots_utils import make_fonts_url, make_minio_img_url, \
    make_recipes_background_url, com_lbl_green

from dotenv import load_dotenv
from asyncio import Semaphore

# 加载 .env 文件
load_dotenv()

# 原数据目录

x_api_key = os.getenv("X_API_KEY")
api_url = os.getenv("API_URL")

# 控制最多同时打开多少个页面
MAX_CONCURRENT_PAGES = 4


async def process_recipes(recipes: dict, food_list: list, env: Environment, browser, screenshot_dir: Path,
                          semaphore: Semaphore, font_server_port: int):
    async with semaphore:
        recipes = make_fonts_url(recipes, font_server_port)

        food_result = []

        parts = []
        if recipes.get("useDescription"):
            parts.append(recipes["useDescription"])
        if recipes.get("buffs"):
            parts.append(recipes["buffs"])

        recipes["effect"] = "<br>".join(parts)

        make_recipes_background_url(recipes)

        for ingredient in recipes['ingredients']:
            # 从food_list中根据ingredient的ingredientKey属性的值，过滤出foodKey属性相同的
            key = ingredient['ingredientKey']
            # 从 food_list 中过滤出 foodKey 相等的元素
            matched = [food for food in food_list if food['foodKey'] == key]

            for food in matched:
                this_food_result = {'foodName': food['foodName'], 'foodIcon': food['foodIcon'],
                                    'amount': ingredient['ingredientNum']}

            food_result.append(this_food_result)

        recipes["food_result"] = food_result or None

        template = env.get_template("template-recipes.html")
        html_content = template.render(**recipes)

        page = await browser.new_page(device_scale_factor=2)
        await page.set_content(html_content, timeout=600000)

        locator = page.locator(".card")
        screenshot_path = screenshot_dir / f"{recipes['recipesName']}.png"
        await locator.screenshot(path=str(screenshot_path))
        await page.close()


async def make_all_recipes_image():
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

        response = httpx.get(f'{api_url}/recipes', headers=headers)
        data = response.json()
        recipes_list = data['data']

        response_food = httpx.get(f'{api_url}/food', headers=headers)
        data_food = response_food.json()
        food_list = data_food['data']

        recipes_list = [w for w in recipes_list if w["recipesName"] not in files]

        template_dir = Path(__file__).parent.parent.parent / "templates"
        env = Environment(loader=FileSystemLoader(str(template_dir)))
        env.filters['com_lbl_green'] = com_lbl_green

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            semaphore = Semaphore(MAX_CONCURRENT_PAGES)

            tasks = [
                process_recipes(recipes, food_list, env, browser, screenshot_dir, semaphore, font_server_port)
                for recipes in recipes_list
            ]
            await asyncio.gather(*tasks)

            await browser.close()
    finally:
        server.stop()


if __name__ == "__main__":
    asyncio.run(make_all_recipes_image())
