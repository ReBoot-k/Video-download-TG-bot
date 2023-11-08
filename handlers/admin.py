from aiogram.dispatcher import FSMContext
from aiogram.types import ContentType
from datetime import datetime, timedelta
import keyboard
from create_bot import *
import states


@dp.message_handler(commands='send_message', is_admin=True)
async def send_message(message: tp.Message, state: FSMContext):
    await message.answer(
        'Напишите сообщение которое вы хотите отправить пользователям',
        reply_markup=keyboard.keyboard_cansel
    )
    await state.set_state(states.SendMessage.write_mes)


@dp.callback_query_handler(text='cansel', state=states.SendMessage.write_mes, is_admin=True)
async def cansel(call: tp.CallbackQuery, state: FSMContext):
    await state.finish()
    await call.message.answer('Отправка отменена')


@dp.message_handler(content_types=ContentType.PHOTO, state=states.SendMessage.write_mes, is_admin=True)
async def send_message(message: tp.Message, state: FSMContext):
    await state.finish()
    file_id = message.photo[-1]['file_id']
    text = message.caption
    for user_id in bd.get_all_user_id():
        if bd.user_have_sub(user_id):
            continue
        else:
            await bot.send_photo(
                user_id,
                photo=file_id,
                caption=text
                )
    for admin_id in config.ADMIN_ID:
        await bot.send_message(admin_id, 'Пользователям без подписки было отправлено такое сообщение')
        await bot.send_photo(
            admin_id,
            photo=file_id,
            caption=text
        )


@dp.message_handler(commands='stat', is_admin=True)
async def send_message(message: tp.Message, state: FSMContext):
    stat = bd.get_statistic()
    await message.answer(
        f'Статистика:\n\nВсего пользователей - {stat["all_user_len"]}\n'
        f'Из них имеет подписку - {stat["all_user_sub"]}'
    )


@dp.message_handler(state=states.SendMessage.write_mes, is_admin=True)
async def send_message(message: tp.Message, state: FSMContext):
    await state.finish()
    text = message.text
    for user_id in bd.get_all_user_id():
        if bd.user_have_sub(user_id):
            continue
        else:
            await bot.send_message(user_id, text)
    for admin_id in config.ADMIN_ID:
        await bot.send_message(admin_id, 'Пользователям без подписки было отправлено такое сообщение')
        await bot.send_message(admin_id, text)


@dp.message_handler(commands='add_tg', is_admin=True)
async def add_channel_tg(message: tp.Message, state: FSMContext):
    text = message.get_args().split(' ')
    if len(text) != 2:
        await message.answer(f'Неправильная команда, нужно писать /add_tg <айди_канала> <ссылка>')
        return
    await message.answer(
        f'Был добавлен канал для подписки:\n   ID - {text[0]}\n   LINK - {text[1]}\n\n'
        f'\n/del_tg - удалить канал\n/get_tg - Посмотреть список каналов'
    )
    bd.add_channel_tg(text[0], text[1])


@dp.message_handler(commands='get_tg', is_admin=True)
async def add_channel_tg(message: tp.Message, state: FSMContext):
    channels = bd.get_channel_list()
    tg_list = ''
    for i in channels:
        tg_list = tg_list + f'    {i[0]} - {i[1]}\n'
    await message.answer(
        f"Вот список каналов для подписки\n\n{tg_list}"
        f"\n/add_tg - добавить канал\n/del_tg - удалить канал"
    )


@dp.message_handler(commands='add_sub', is_admin=True)
async def add_channel_tg(message: tp.Message, state: FSMContext):
    text = message.get_args().split(' ')

    if len(text) != 2:
        await message.answer(
            f'Неправильная команда, нужно писать /add_sub <юзер_айди> <количесво месецев подписки>'
        )
        return

    sub_time = datetime.now() + timedelta(days=int(text[1]) * 30)
    sub_time = int(sub_time.timestamp())
    bd.subscribe_user(text[0], sub_time)
    sub_time = bd.get_subscription(message.from_user.id)
    sub_time_str = datetime.utcfromtimestamp(sub_time).strftime('%d-%m-%Y')

    await message.answer(
        f"{text[0]}: ✅ Подписка активирована до {sub_time_str}\n\n"
        f"/del_sub <юзер_айди> - Если хотите отменить подписку до срока окончания"
    )


@dp.message_handler(commands='del_sub', is_admin=True)
async def del_sub(message: tp.Message, state: FSMContext):
    text = message.get_args()
    if len(text) == 0:
        await message.answer(f'Неправильная команда, нужно писать /del_sub <юзер_айди>')
        return
    bd.unsubscribe_user(text)
    await message.answer(f'{text}: У пользователя больше нет подписки')


@dp.message_handler(commands='del_tg', is_admin=True)
async def add_channel_tg(message: tp.Message, state: FSMContext):
    text = message.get_args()
    if len(text) == 0:
        await message.answer(f'Неправильная команда, нужно писать /del_tg <айди_канала>')
        return
    bd.del_channel(text)

    await message.answer(
        f'Был удален канал под айди - {text}\n\n'
        f'/get_tg - Посмотреть список каналов\n/add_tg - добавить канал'
    )