import asyncio
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from playwright.async_api import async_playwright

from models import CookRecipesDataTable, RecipesIngredients, IngredientData
from utils.font_server import FontServer
from utils.screenshots_utils import make_fonts_url, make_minio_img_url, \
     make_recipes_background_url, com_lbl_green
from tortoise import Tortoise

from config import database_config
from asyncio import Semaphore


# 控制最多同时打开多少个页面
MAX_CONCURRENT_PAGES = 4

async def process_recipes(recipes: dict, env: Environment, browser, screenshot_dir: Path, semaphore: Semaphore, font_server_port: int):
    async with semaphore:
        recipes = make_fonts_url(recipes, font_server_port)
        recipes['recipes_icon'] = make_minio_img_url(recipes['recipes_icon'])

        ingredient_result = []

        recipes['effect'] = f'{recipes["use_description"]}，{recipes["buffs"]}'

        make_recipes_background_url(recipes)

        recipes_ingredients = await RecipesIngredients.filter(
            recipes_id=recipes["recipes_id"]).values("ingredient_id", "amount")

        for ingredient in recipes_ingredients:
            this_ingredient_info = await IngredientData.filter(
                ingredient_id=ingredient["ingredient_id"]).values("ingredient_name", "ingredient_icon")

            this_ingredient_result = {'ingredient_name': this_ingredient_info[0]['ingredient_name'], 'ingredient_icon': make_minio_img_url(this_ingredient_info[0]['ingredient_icon']), 'amount': ingredient['amount']}

            ingredient_result.append(this_ingredient_result)

        recipes["ingredient_result"] = ingredient_result or None

        template = env.get_template("template-recipes.html")
        html_content = template.render(**recipes)

        page = await browser.new_page()
        await page.set_content(html_content, timeout=600000)

        locator = page.locator(".card")
        screenshot_path = screenshot_dir / f"{recipes['recipes_name']}.png"
        await locator.screenshot(path=str(screenshot_path))
        await page.close()

async def make_all_recipes_image():
    font_server_port = 2288
    font_dir = Path(__file__).parent.parent / "assets" / "fonts"
    server = FontServer(str(font_dir), port=font_server_port)
    server.start()

    try:
        await Tortoise.init(config=database_config.TORTOISE_ORM)

        screenshot_dir = Path(__file__).parent.parent / "dist" / "screenshots" / "recipes"
        screenshot_dir.mkdir(exist_ok=True)
        files = [file.stem for file in screenshot_dir.iterdir() if file.is_file()]

        recipes_list = await CookRecipesDataTable.all().values("recipes_id", "recipes_name", "recipes_des", "recipes_icon", "use_description", "buffs")

        recipes_list = [w for w in recipes_list if w["recipes_name"] not in files]

        template_dir = Path(__file__).parent.parent / "templates"
        env = Environment(loader=FileSystemLoader(str(template_dir)))
        env.filters['com_lbl_green'] = com_lbl_green

        async with async_playwright() as p:
            browser = await p.firefox.launch(headless=True)
            semaphore = Semaphore(MAX_CONCURRENT_PAGES)

            tasks = [
                process_recipes(recipes, env, browser, screenshot_dir, semaphore, font_server_port)
                for recipes in recipes_list
            ]
            await asyncio.gather(*tasks)

            await browser.close()
    finally:
        server.stop()




if __name__ == "__main__":
    asyncio.run(make_all_recipes_image())
