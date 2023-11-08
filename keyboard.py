from aiogram import types as tp
from aiogram.utils.callback_data import CallbackData

tariffs_data = CallbackData("tariff", "months", "amount")

keyboard_tariffs = tp.InlineKeyboardMarkup(row_width=1)

tariffs_buttons = [
    tp.InlineKeyboardButton(text="Месяц - 5$", callback_data=tariffs_data.new(1, 5)),
]
keyboard_tariffs.add(*tariffs_buttons)

keyboard_cansel = tp.InlineKeyboardMarkup(row_width=1).add(tp.InlineKeyboardButton(text="отмена", callback_data='cansel'))


def create_keyboard_resolution(resolutions, sizes):

    keyboard_resolution = tp.InlineKeyboardMarkup(row_width=2)
    for resolution, size in zip(resolutions, sizes):
        keyboard_resolution.add(
            tp.InlineKeyboardButton(
                text="{} ({})".format(resolution, size),
                callback_data="{}:{}".format(resolution, size),
            )
        )



    keyboard_resolution.add(
        tp.InlineKeyboardButton(text='Отмена', callback_data="cansel")
    )


    return keyboard_resolution