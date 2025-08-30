import asyncio
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from playwright.async_api import async_playwright

from models import  FashionData
from utils.font_server import FontServer
from utils.screenshots_utils import make_fonts_url, make_minio_img_url, \
    make_recipes_background_url, com_lbl_green, highlight_shuzhi
from tortoise import Tortoise

from config import database_config
from asyncio import Semaphore


# 控制最多同时打开多少个页面
MAX_CONCURRENT_PAGES = 4

async def process_fashion(fashion: dict, env: Environment, browser, screenshot_dir: Path, semaphore: Semaphore, font_server_port: int):
    async with semaphore:
        fashion = make_fonts_url(fashion, font_server_port)

        for i, icon in enumerate(fashion['icons']):
            fashion['icons'][i] = make_minio_img_url(icon)


        template = env.get_template("template-fashion.html")
        html_content = template.render(**fashion)

        page = await browser.new_page()
        await page.set_content(html_content, timeout=600000)

        locator = page.locator(".card")
        screenshot_path = screenshot_dir / f"{fashion['fashion_name']}.png"
        await locator.screenshot(path=str(screenshot_path))
        await page.close()

async def make_all_fashion_image():
    font_server_port = 2288
    font_dir = Path(__file__).parent.parent / "assets" / "fonts"
    server = FontServer(str(font_dir), port=font_server_port)
    server.start()

    try:
        # await Tortoise.init(config=database_config.TORTOISE_ORM)

        screenshot_dir = Path(__file__).parent.parent / "dist" / "screenshots" / "fashion"
        screenshot_dir.mkdir(exist_ok=True)
        files = [file.stem for file in screenshot_dir.iterdir() if file.is_file()]

        fashion_list = await FashionData.all().values("fashion_name", "description", "active_source", "icons")

        fashion_list = [w for w in fashion_list if w["fashion_name"] not in files]

        template_dir = Path(__file__).parent.parent / "templates"
        env = Environment(loader=FileSystemLoader(str(template_dir)))

        # env.filters['com_lbl_green'] = com_lbl_green
        # env.filters['highlight_shuzhi'] = highlight_shuzhi

        async with async_playwright() as p:
            browser = await p.firefox.launch(headless=True)
            semaphore = Semaphore(MAX_CONCURRENT_PAGES)

            tasks = [
                process_fashion(fashion, env, browser, screenshot_dir, semaphore, font_server_port)
                for fashion in fashion_list
            ]
            await asyncio.gather(*tasks)

            await browser.close()
    finally:
        server.stop()




if __name__ == "__main__":
    asyncio.run(make_all_fashion_image())
