import logging

from aiogram import Bot, Dispatcher
from aiogram.bot.api import TelegramAPIServer
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import bdfunk
import os
from filters import *
import servise

insta = servise.InstaLoader()
youtube = servise.YouTubeLoader()
tiktok = servise.TikTokLoader()

PAY_TOKEN = os.environ.get('PAYMENT_TOKEN')

local_server = TelegramAPIServer.from_base('http://127.0.0.1:8081')

bot = Bot(config.BOT_TOKEN, server=local_server)
dp = Dispatcher(bot, storage=MemoryStorage())

dp.bind_filter(MyFilterAdmin)
logging.basicConfig(level=logging.INFO)
bd = bdfunk.DataBase('DataBase.db')
