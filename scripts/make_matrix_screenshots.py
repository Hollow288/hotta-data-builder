import asyncio
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from playwright.async_api import async_playwright

from models import  Matrix, SuitUnactivateDetail
from utils.font_server import FontServer
from utils.screenshots_utils import make_fonts_url, make_minio_img_url,  \
    highlight_shuzhi, make_matrix_background_url
from tortoise import Tortoise

from config import database_config
from asyncio import Semaphore


# 控制最多同时打开多少个页面
MAX_CONCURRENT_PAGES = 4

async def process_matrix(matrix: dict, env: Environment, browser, screenshot_dir: Path, semaphore: Semaphore, font_server_port: int):
    async with semaphore:
        matrix = make_fonts_url(matrix, font_server_port)
        matrix['suit_icon'] = make_minio_img_url(matrix['suit_icon'])

        make_matrix_background_url(matrix)

        suit_unactivate_detail = await SuitUnactivateDetail.filter(
            matrix_id=matrix["matrix_id"]).values("item_name", "item_describe")

        matrix["suit_unactivate_detail"] = suit_unactivate_detail or None

        template = env.get_template("template-matrix.html")
        html_content = template.render(**matrix)

        page = await browser.new_page()
        await page.set_content(html_content, timeout=600000)

        locator = page.locator(".card")
        screenshot_path = screenshot_dir / f"{matrix['suit_name']}.png"
        await locator.screenshot(path=str(screenshot_path))
        await page.close()

async def make_all_matrix_image():
    font_server_port = 2288
    font_dir = Path(__file__).parent.parent / "assets" / "fonts"
    server = FontServer(str(font_dir), port=font_server_port)
    server.start()

    try:
        # await Tortoise.init(config=database_config.TORTOISE_ORM)

        screenshot_dir = Path(__file__).parent.parent / "dist" / "screenshots" / "matrix"
        screenshot_dir.mkdir(exist_ok=True)
        files = [file.stem for file in screenshot_dir.iterdir() if file.is_file()]

        matrix_list = await Matrix.all().values("matrix_id", "matrix_suit_quality", "suit_name", "suit_icon")

        matrix_list = [w for w in matrix_list if w["suit_name"] not in files]

        template_dir = Path(__file__).parent.parent / "templates"
        env = Environment(loader=FileSystemLoader(str(template_dir)))
        env.filters['highlight_shuzhi'] = highlight_shuzhi

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            semaphore = Semaphore(MAX_CONCURRENT_PAGES)

            tasks = [
                process_matrix(matrix, env, browser, screenshot_dir, semaphore, font_server_port)
                for matrix in matrix_list
            ]
            await asyncio.gather(*tasks)

            await browser.close()
    finally:
        server.stop()




if __name__ == "__main__":
    asyncio.run(make_all_matrix_image())
