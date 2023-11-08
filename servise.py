import logging

import requests
from bs4 import BeautifulSoup
import pyshorteners
import asyncio
from pyppeteer import launch
from pyppeteer.page import Page
from pyppeteer.element_handle import ElementHandle

from config import NOT_CALCULATED
import urllib.request
import re

import aiohttp
import aiofiles

logging.getLogger('pyppeteer').setLevel(logging.ERROR)



class InstaLoader:

    def get_code_video(self, link):
        return link.split('/')[link.split('/').index('reels')+1]

    async def get_direct_link_reels(self, link: str) -> str:
        browser = await launch(options={'args': ['--no-sandbox'], 'headless': True})

        try:
            page: Page = await browser.newPage()
            await page.goto('https://igdownloader.app/ru/download-instagram-reels')

            url: ElementHandle = await page.querySelector('#s_input')
            await url.type(link)

            await url.press('Enter')
            await page.waitFor(3000)

            download_button = await page.waitForSelector('#closeModalBtn')
            await download_button.click()

            direct_link = await page.querySelectorEval('#download-result > ul > li > div > div.download-items__btn > a',
                                                       'element => element.getAttribute("href")')
            return direct_link
        finally:
            await browser.close()


    def download_reels(self, direct_link, path):
        """
        Downloads the Insta video from the provided direct link and saves it to the specified path.
        """
        response = requests.get(direct_link)

        with open(path, "wb") as f:
            f.write(response.content)
        return None


class TikTokLoader:

    async def get_download_link_tiktok(self, link):
        """
        Opens the snaptik.app website, enters the link, and retrieves the download link for the TikTok video.
        """
        browser = await launch(options={'args': ['--no-sandbox'], 'headless': True})

        page = await browser.newPage()
        try:
            await page.goto('https://snaptik.app')
            url: ElementHandle = await page.querySelector('#url')
            await url.type(link)

            await url.press('Enter')
            await page.waitFor(1000)

            await page.waitForSelector('#download > div > div.video-links > a:nth-child(1)')
            download_link = await page.querySelectorEval('#download > div > div.video-links > a:nth-child(1)',
                                                         'el => el.href')

            return download_link
        except Exception as e:
            print(f"Error: {e}")
            return False
        finally:
            await browser.close()

    def download_video_tiktok(self, direct_link: str, path: str):
        """
        Downloads the TikTok video from the provided direct link and saves it to the specified path.
        """
        response = requests.get(direct_link)

        with open(path, "wb") as f:
            f.write(response.content)
        return None

    def get_tiktok_video_id(self, link):
        code = link.split('/')[-1]
        if '?' in code:
            code = code[:code.index('?')]
        return code


class YouTubeLoader:
    async def get_video_info_youtube(self, youtube_link: str):
        """
        Opens the save.tube website, enters the YouTube link, and retrieves video information.
        """
        browser = await launch(options={'args': ['--no-sandbox'], 'headless': True})
        page = await browser.newPage()
        try:
            await page.goto('https://save.tube')
            await asyncio.sleep(1.5)
            await page.waitForSelector('#video')
            await page.focus('#video')
            await page.keyboard.type(youtube_link)
            await page.keyboard.press('Enter')

            return await self.get_video_info_from_page(page)

        except Exception as e:
            print(f"Error: {e}")
            return False
        finally:
            await browser.close()


    '''def download_video_youtube(self, direct_link: str, path: str):
        """
        Downloads the youtube video from the provided direct link and saves it to the specified path.
        """
        urllib.request.urlretrieve(direct_link, path)'''


    async def download_video_youtube(self, direct_link: str, path: str):
        """
        Downloads the youtube video from the provided direct link and saves it to the specified path asynchronously.
        """
        async with aiohttp.ClientSession() as session: 
            async with session.get(direct_link, timeout=None) as response: 
                file_data = await response.read()
                async with aiofiles.open(path, "wb") as file:
                    await file.write(file_data)


    async def get_video_info_from_page(self, page: Page):
        await page.waitForSelector(".video-info")
        video_info_html = await page.querySelectorEval(".video-info", "el => el.outerHTML")

        soup = BeautifulSoup(video_info_html, "lxml")
        video_info = {}

        title = soup.find("h2", {"class": "title ellipsis"})
        video_info["title"] = title.text if title else ""

        image_html = soup.find("img", {"src": True})
        video_info["image_url"] = image_html["src"] if image_html else ""

        duration_element = soup.find("p", {"class": "video-duration"})
        video_info["duration"] = duration_element.text if duration_element else ""

        soup = BeautifulSoup(await page.content(), "lxml")

        resolv_rows = soup.find_all("div", class_="row")
        resolv_rows.pop(0)
        video_info["resolv_list"] = []
        video_info["size_list"] = []

        compile_codec = re.compile("video codec: (avc1|mp4v)")
        compile_type = re.compile("mp4|3gp")
        compile_size = re.compile("MB|KB|GB|TB")

        for row in resolv_rows:
            resol_row = row.find("div", {"title": compile_codec})
            
            if resol_row:
                resol_row = resol_row.text[: resol_row.text.index("p") + 1]

                type_file = row.find("div", text=compile_type)

                if type_file:
                    size_element = type_file.find_next_sibling()
                    size_element = (
                        size_element.text
                        if size_element
                        else NOT_CALCULATED
                    )

                    
                    if resol_row not in video_info["resolv_list"]:
                        video_info["resolv_list"].append(resol_row)
                    else:
                        continue

                    size_element = re.sub("</?div>", "", size_element)
                    video_info["size_list"].append(size_element)

        # Из-за особенностей save.tube качество 240p иногда попадает в конец списка.
        # Меням местами последний и предпоследний элемент
        # Нужно поменять и список размеров файлов
        if "480p" in video_info["resolv_list"] and video_info["resolv_list"][-1] == "240p":
            video_info["resolv_list"][-1], video_info["resolv_list"][-2] = (
                video_info["resolv_list"][-2],
                video_info["resolv_list"][-1],
            )
            video_info["size_list"][-1], video_info["size_list"][-2] = (
                video_info["size_list"][-2],
                video_info["size_list"][-1],
            )
            
        return video_info


    async def get_download_link_youtube(self, youtube_link: str, resolv_required: str) -> str or False:
        """
        Opens the save.tube website, enters the YouTube link, and retrieves the download link for the specified resolution.
        """
        browser = await launch(options={'args': ['--no-sandbox'], 'headless': True})
        page = await browser.newPage()
        try:
            await page.goto('https://save.tube')
            await asyncio.sleep(1.5)
            await page.waitForSelector('#video')
            await page.focus('#video')
            await page.keyboard.type(youtube_link)
            await page.keyboard.press('Enter')

            await page.waitForSelector('.video-info')
            return await self.get_download_link_from_page(page, resolv_required)

        except Exception as e:
            print(f"Error: {e}")
            return False
        finally:
            await browser.close()

    async def get_download_link_from_page(self, page: Page, resolv_required: str):
        page_content = await page.content()
        soup = BeautifulSoup(page_content, 'lxml')
        resolv_rows = soup.find_all('div', class_='row')
        resolv_rows.pop(0)

        for row in resolv_rows:
            resol_row = row.find('div', {'title': re.compile('video codec: (avc1|mp4v)')})

            type_file = row.find('div', text=re.compile('mp4|3gp'))
            
            if resol_row:
                resol_row = resol_row.text
                resol_row = resol_row[:resol_row.index('p') + 1]

            if resol_row == resolv_required and type_file:
                download_url = row.find('a', class_='downloadBtn')['href']
                return download_url

        return False


def shorten_url(url):
    s = pyshorteners.Shortener()
    short_url = s.tinyurl.short(url)
    return short_url

