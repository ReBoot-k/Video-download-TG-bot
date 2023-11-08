from aiogram.dispatcher.filters.state import StatesGroup, State


class SendTikTok(StatesGroup):
    send_tiktok = State()


class SendYoutube(StatesGroup):
    send_youtube = State()
    set_resol = State()


class SendReels(StatesGroup):
    send_reels = State()


class Sub(StatesGroup):
    sub_channel = State()
    have_sub = State()


class SendMessage(StatesGroup):
    write_mes = State()


class AddChannel(StatesGroup):
    verif_info = State()