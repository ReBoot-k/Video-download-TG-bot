import time
from datetime import datetime

from aiogram import types as tp
from aiogram.dispatcher import FSMContext

import keyboard

from create_bot import dp, bot, bd


@dp.message_handler(commands='start')
async def start(message: tp.Message):
    if not bd.check_for_presence_in_the_list(message.from_user.id):
        bd.add_guests(message.from_user.id, message.from_user.username)
        bd.update_date(message.from_user.id)
    await message.answer(
        'Здравствуйте!👋🏻 Я бот коротый поможет вам в повседневной работе медиа в соц-сетях.\n'
        'Я могу скачивать видео с таких приложений как YouTube, Instagram Reels, TikTok, YouTube Shorts.\n\n'
        '   /balance - посмотреть количесво доступных скачиваний\n\nДля начала скачивания просто скиньте мне нужную ссылку'
    )


@dp.message_handler(commands='balance')
async def balance(message: tp.Message):
    if bd.need_update_limit(message.from_user.id):
        bd.update_date(message.from_user.id)
    free_work = bd.work_limit(message.from_user.id)
    sub_time = bd.get_subscription(message.from_user.id)
    if sub_time is not None:
        if int(time.time()) < sub_time:
            sub_time_str = datetime.utcfromtimestamp(sub_time).strftime('%d-%m-%Y')
            await message.answer(f"✅ Подписка активирована до {sub_time_str}\n\n")
    else:
        await message.answer(
            f'У вас есть еще {free_work} бесплатных скачиваний на сегодня\n\n'
            f'Если хотите использовать бота без ограничений вызовите команду - /sub\n'
        )


@dp.message_handler(commands='help')
async def balance(message: tp.Message, state: FSMContext):
    await state.finish()
    await message.answer(
        'Похоже у вас возникла ошибка, я обновил свои конфигурации, проверьте ушла ли ошибка.'
        '\nЕсли все еще что-то мешает вам работать, можете обратится к владельцам бота - @fierka'
    )