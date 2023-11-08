import re

from aiogram.dispatcher.filters import BoundFilter
from aiogram import types as tp
import config


class MyFilterAdmin(BoundFilter):
    key = 'is_admin'

    def __init__(self, is_admin):
        self.is_admin = is_admin

    async def check(self, message: tp.Message):
        if int(message.from_user.id) in config.ADMIN_ID:
            return True
        else:
            return False


class TikTokLinkFilter(BoundFilter):
    key = 'is_link_tiktok'

    def __init__(self, is_link_tiktok):
        self.is_link_tiktok = is_link_tiktok

    async def check(self, message: tp.Message):
        tiktok_pattern = r"tiktok\.com"
        if re.search(tiktok_pattern, message.text.strip()):
            return True
        else:
            return False


class LinkFilter(BoundFilter):
    key = 'is_link_tiktok'

    def __init__(self, is_link_tiktok):
        self.is_link_tiktok = is_link_tiktok

    async def check(self, message: tp.Message):
        tiktok_pattern = r"tiktok\.com"
        if re.search(tiktok_pattern, message.text.strip()):
            return True
        else:
            return False