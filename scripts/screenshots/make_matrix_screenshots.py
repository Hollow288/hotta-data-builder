import asyncio
import os

import httpx
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from playwright.async_api import async_playwright

from utils.font_server import FontServer
from utils.screenshots_utils import make_fonts_url, make_minio_img_url, \
    highlight_shuzhi, make_matrix_background_url

from dotenv import load_dotenv
from asyncio import Semaphore

x_api_key = os.getenv("X_API_KEY")
api_url = os.getenv("API_URL")

# 控制最多同时打开多少个页面
MAX_CONCURRENT_PAGES = 4


async def process_matrix(matrix: dict, env: Environment, browser, screenshot_dir: Path, semaphore: Semaphore,
                         font_server_port: int):
    async with semaphore:
        matrix = make_fonts_url(matrix, font_server_port)

        make_matrix_background_url(matrix)

        template = env.get_template("template-matrix.html")
        html_content = template.render(**matrix)

        page = await browser.new_page(device_scale_factor=2)
        await page.set_content(html_content, timeout=600000)

        locator = page.locator(".card")
        screenshot_path = screenshot_dir / f"{matrix['matrixName']}.png"
        await locator.screenshot(path=str(screenshot_path))
        await page.close()


async def make_all_matrix_image():
    font_server_port = 2288
    font_dir = Path(__file__).parent.parent.parent / "assets" / "fonts"
    server = FontServer(str(font_dir), port=font_server_port)
    server.start()

    try:

        screenshot_dir = Path(__file__).parent.parent.parent / "dist" / "screenshots" / "matrix"
        screenshot_dir.mkdir(exist_ok=True)
        files = [file.stem for file in screenshot_dir.iterdir() if file.is_file()]

        headers = {
            "Content-Type": "application/json",
            "X-API-KEY": x_api_key,
        }

        response = httpx.get(f'{api_url}/matrix', headers=headers)

        data = response.json()

        matrix_list = data['data']

        matrix_list = [w for w in matrix_list if w["matrixName"] not in files]

        template_dir = Path(__file__).parent.parent.parent / "templates"
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
