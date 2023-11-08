from aiogram.dispatcher import FSMContext
import keyboard as kb
import states
from create_bot import *
from config import MAX_SIZE_FILE
from config import NOT_CALCULATED

import secrets
import pickle
import requests
import os
import asyncio

video_dict = {}
try:
    with open("video_dict.pkl", "rb") as f:
        video_dict = pickle.load(f)
except FileNotFoundError:
    pass

def convert_to_kb(string):
    if string == NOT_CALCULATED:
        return 0

    factors = {'B': 0.001, 'KB': 1, 'MB': 1024, 'GB': 1024**2, 'TB': 1024**3}
    number, unit = string.split()
    number = float(number)

    if unit in factors:
        return number * factors[unit]
    else:
        return 0

@dp.message_handler(lambda message: any(word in message.text for word in ['instagram.com', 'youtube.com', 'youtu.be', 'tiktok.com']))
async def download(message: tp.Message, state: FSMContext):
    if await check_if_may_download(message, state):
        if 'instagram.com' in message.text:
            await download_reels(message)
        elif 'youtube.com' in message.text or 'youtu.be' in message.text:
            await download_youtube(message, state)
        elif 'tiktok.com' in message.text:
            await download_tiktok(message)


@dp.message_handler(lambda message: any(word in message.text.lower() for word in ['instagram.com', 'youtube.com', 'youtu.be', 'tiktok.com']),
                    state=states.Sub.have_sub)
async def download_after_sub(message: tp.Message, state: FSMContext):
    if await check_if_may_download(message, state):
        if 'instagram.com' in message.text:
            await download_reels(message)
        elif 'youtube.com' in message.text or 'youtu.be' in message.text:
            await download_youtube(message, state)
        elif 'tiktok.com' in message.text:
            await download_tiktok(message)


async def get_tg_channel(user_id):
    channels_list = bd.get_channel_list()
    for channel in channels_list:
        user_channel_status = await bot.get_chat_member(chat_id=int(channel[0]), user_id=user_id)
        if user_channel_status['status'] == 'left':
            return channel
        else:
            continue
    return False


async def get_tg_for_sub(message: tp.Message, state: FSMContext):
    await state.finish()
    if await state.get_state() == states.Sub.have_sub:
        await state.finish()
        return True

    aviable_channel = await get_tg_channel(message.from_user.id)

    if aviable_channel is False:
        return True

    keyboard_sub = tp.InlineKeyboardMarkup(row_width=1).add(
        tp.InlineKeyboardButton(text='Cсылка 📨', url=aviable_channel[1]),
        tp.InlineKeyboardButton(text='Я подписался ✅', callback_data='look_sub'),
    )
    await state.set_state(states.Sub.sub_channel)
    await state.update_data(channel_id=aviable_channel[0])
    await message.answer('Сначала вам нужно подписатся на канал', reply_markup=keyboard_sub)
    return False


async def check_if_may_download(message: tp.Message, state: FSMContext):
    if bd.user_have_sub(message.from_user.id):
        return True
    if bd.need_update_limit(message.from_user.id):
        bd.update_date(message.from_user.id)
    if bd.work_limit(message.from_user.id) in [3, 1]:
        return await get_tg_for_sub(message, state)

    elif bd.work_limit(message.from_user.id) == 0:
        await message.answer('На сегодня безплатный лимит закончился. Уберите лимит вызвав команду /sub')
        return False
    else:
        return True


@dp.callback_query_handler(text='look_sub', state=states.Sub.sub_channel)
async def look(call: tp.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await state.finish()
    user_channel_status = await bot.get_chat_member(chat_id=data['channel_id'], user_id=call.from_user.id)
    if user_channel_status['status'] != 'left':
        await call.message.answer('Подписка подтверждена, отправьте ссылку повторно')

        await state.set_state(states.Sub.have_sub)
    else:
        await call.message.answer('Вас нет в подпишиках этого канала, отправьте ссылку еще раз и повторите попытку')


async def download_reels(message: tp.Message):
    await message.answer('Загрузка . . .')
    direct_link = await insta.get_direct_link_reels(message.text)

    if direct_link is False:
        await message.answer(
            'Возникла ошибка, не могу скачать это, проверьте правильность ссылки.\n\n'
            'Вызовите /help для получения дополнительной информации.')
        return

    path = 'reels/' + insta.get_code_video(message.text) + '.mp4'
    insta.download_reels(direct_link, path)

    if os.path.isfile(path):
        await message.answer_video(
            caption='✅ Готово, вот скачанное видео',
            video=open(path, 'rb'),
        )
        os.remove(path)

    await rest_free_downloads(message.from_user.id)


async def download_youtube(message: tp.Message, state: FSMContext):
    await message.answer('Загрузка . . .')
    video_info = await youtube.get_video_info_youtube(message.text)

    if video_info is False:
        await message.answer('Возникли проблемы при загрузке, повторите попытку позже или обратитесь за помощью(/help)')
        return
  
    keyboard = kb.create_keyboard_resolution(video_info['resolv_list'], video_info['size_list'])

    response = requests.get(video_info['image_url'])

    caption = await message.answer_photo(
        photo=response.content,
        caption=f"{video_info['title']}\n\n Длительность: {video_info['duration']}🕔\n\nВыберите разрешение⬇️",
        reply_markup=keyboard
    )
    await state.set_state(states.SendYoutube.set_resol)
    await state.update_data(url=message.text)
    await state.update_data(caption=caption)


async def update_caption(message, path, max_size):
    percent = 0
    percent_last = -1
    size = 0
    while percent <= 90:
        if percent == "неизвестно":
            break

        if os.path.isfile(path):
            size = os.path.getsize(path) / 1024

        if max_size == 0:
            percent = "неизвестно"
        else:
            
            number = round((size * 100) / max_size, 1)
            print(number, size, max_size)
            if number <= 30:
                percent = 0
            elif number <= 70:
                percent = 30
            elif number <= 90:
                percent = 70
            else:
                percent = 90

        
        caption = f"Скачано >{percent}%"
        if percent_last < percent:
            await message.edit_caption(message.caption + "\n" + caption)

        percent_last = percent
        await asyncio.sleep(3) 

    
                   

@dp.callback_query_handler(state=states.SendYoutube.set_resol)
async def get_result_youtube(call: tp.CallbackQuery, state: FSMContext):
    data_video = await state.get_data()
    await state.finish()

    caption = data_video['caption'].caption
    text_res = caption[:caption.find('Выберите разрешение⬇️')]
    
    chat_id = call.message.chat.id

    if call.data.split(":")[0] == 'cansel':
        await call.message.answer('Скачивание отменено')
        return

    resolution, size = call.data.split(':')
    size = convert_to_kb(size)

    if resolution in ['1440p', '2160p'] and not bd.user_have_sub(call.from_user.id):
        await data_video['caption'].delete_reply_markup()
        await call.message.answer(
            'Максимальное разрешение при бесплатном тарифе - 1080р\n\n'
            'Уберите лимит вызвав команду /sub'
        )
        return
    
    if (data_video['url'], resolution) in video_dict:
        await bot.send_video(chat_id=chat_id, 
                             video=video_dict[data_video['url'], resolution],
                             caption=text_res
        )
        return

    MAX_SIZE_KB = convert_to_kb(MAX_SIZE_FILE)
    if size <= MAX_SIZE_KB:
        
        await data_video['caption'].edit_caption(
            text_res + '\n\n⏰ Подготовка видео, подождите пожалуйста...'
        )
        video_info = await youtube.get_download_link_youtube(
            data_video['url'], resolution
        )

        path = 'video/' + secrets.token_urlsafe() + '.mp4'

        print('download...', resolution, size)
        task = asyncio.create_task(update_caption(data_video['caption'], path, size))
        await youtube.download_video_youtube(video_info, path)
        print('sending...')



        if os.path.isfile(path):
            if os.path.getsize(path) / 1024 <= MAX_SIZE_KB:
                video_message = await bot.send_video(chat_id=chat_id, video=open(path, 'rb'), caption=text_res)
                file_id = video_message.video.file_id
                video_dict[(data_video["url"],resolution)] = file_id

                with open("video_dict.pkl", "wb") as f:
                    pickle.dump(video_dict, f)
            else:
                await call.message.answer('Файл оказался слишком велик')
            os.remove(path)

        await rest_free_downloads(call.from_user.id)
    else:
        await call.message.answer(
            text='Файл слишком большой (превышает {})!'.format(MAX_SIZE_FILE),
        )



async def rest_free_downloads(user_id: tp.Message):
    if bd.user_have_sub(user_id) is False:
        bd.use_work(user_id)
        work_limit = bd.work_limit(user_id)
        await bot.send_message(
            user_id,
            'У вас осталось ' + str(work_limit) + ' бесплатных'
            ' скачиваний на сегодня. Чтобы убрать ограничение, вызовите команду /sub'
        )


async def download_tiktok(message: tp.Message):
    await message.answer('Загрузка . . .')
    path = 'tiktok/' + tiktok.get_tiktok_video_id(message.text.strip())+'.mp4'
    direct_link = await tiktok.get_download_link_tiktok(message.text)

    if direct_link is False:
        await message.answer('Возникли проблемы при загрузке, повторите попытку позже или обратитесь за помощью(/help)')
        return

    tiktok.download_video_tiktok(direct_link, path)
    await message.answer_video(
        caption='✅ Готово, вот скачаное видео',
        video=open(path, 'rb'),
    )
    if os.path.isfile(path):
        os.remove(path)

    await rest_free_downloads(message.from_user.id)
