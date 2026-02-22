import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, LabeledPrice
from aiogram.filters import Command

TOKEN = "8555686519:AAGb-AiAYSgm0_mONFr5Hnwg0GfPiRpXyvM"

bot = Bot(token=TOKEN)
dp = Dispatcher()

user_points = {}

products = {
    "buy_1k": {"points": 1000, "price": 10},
    "buy_10k": {"points": 10000, "price": 80},
    "buy_50k": {"points": 50000, "price": 350},
}

@dp.message(Command("start"))
async def start(message: types.Message):

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="شحن 1k نقطة - 10 ⭐", callback_data="buy_1k")],
            [InlineKeyboardButton(text="شحن 10k نقطة - 80 ⭐", callback_data="buy_10k")],
            [InlineKeyboardButton(text="شحن 50k نقطة - 350 ⭐", callback_data="buy_50k")],
        ]
    )

    await message.answer("اختر الكمية للشحن:", reply_markup=keyboard)


@dp.callback_query(F.data.startswith("buy_"))
async def buy(callback: types.CallbackQuery):

    product = products[callback.data]

    prices = [LabeledPrice(
        label=f"{product['points']} نقطة",
        amount=product['price']
    )]

    await bot.send_invoice(
        chat_id=callback.from_user.id,
        title="شراء نقاط",
        description=f"شراء {product['points']} نقطة",
        payload=callback.data,
        provider_token="",
        currency="XTR",
        prices=prices
    )


@dp.pre_checkout_query()
async def checkout(pre_checkout_query: types.PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)


@dp.message(F.successful_payment)
async def success(message: types.Message):

    payload = message.successful_payment.invoice_payload
    points = products[payload]["points"]

    user_id = message.from_user.id

    if user_id not in user_points:
        user_points[user_id] = 0

    user_points[user_id] += points

    await message.answer(
        f"تم الشحن بنجاح ✅\nرصيدك: {user_points[user_id]}"
    )


async def main():
    await dp.start_polling(bot)

asyncio.run(main())
