from aiogram import types as tp
from aiogram.types import LabeledPrice
from datetime import datetime, timedelta
import keyboard as kb

from create_bot import dp, bot, bd, PAY_TOKEN


@dp.message_handler(commands='sub')
async def tarif(message: tp.Message):
    await message.answer(
        'Подписка обеспечивает вам неограниченное использование всех моих функций, и отключает требования подписки на каналы.\n\n'
        'Чтобы подписатся, ввяжитесь с нашим менеджером - @fierka',
    )


@dp.callback_query_handler(kb.tariffs_data.filter())
async def select_tariff(call: tp.CallbackQuery, callback_data: dict):
    months = callback_data["months"]
    amount = int(callback_data["amount"])

    await call.bot.send_invoice(
        call.from_user.id, title="Оплата подписки",
        description="Для оплаты подписки перейдите по ссылке: Оплатить",
        payload=months, provider_token=PAY_TOKEN, currency="USD",
        prices=[LabeledPrice(label="Оплата подписки", amount=amount * 100)]
    )


@dp.pre_checkout_query_handler()
async def approve_order(pre_checkout_query: tp.PreCheckoutQuery):
    await pre_checkout_query.bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)


@dp.message_handler(content_types="successful_payment")
async def process_successful_payment(message: tp.Message):
    sub_time = datetime.now() + timedelta(days=int(message.successful_payment.invoice_payload) * 30)
    sub_time = int(sub_time.timestamp())
    bd.subscribe_user(message.from_user.id, sub_time)

    await message.answer(f"Платеж проведен. Подписка активирована")
