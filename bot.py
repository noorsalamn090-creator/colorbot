import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, LabeledPrice

TOKEN = "8555686519:AAGb-AiAYSgm0_mONFr5Hnwg0GfPiRpXyvM"

bot = Bot(token=TOKEN)
dp = Dispatcher()

user_points = {}

@dp.message(commands=["start"])
async def start(message: types.Message):

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="شراء 1000 نقطة - 10 ⭐", callback_data="buy")]
        ]
    )

    await message.answer("اهلا بك في بوت النقاط\nاضغط الزر للشراء:", reply_markup=keyboard)


@dp.callback_query(lambda c: c.data == "buy")
async def buy(callback: types.CallbackQuery):

    prices = [LabeledPrice(label="1000 نقطة", amount=10)]

    await bot.send_invoice(
        chat_id=callback.from_user.id,
        title="شراء نقاط",
        description="شراء 1000 نقطة",
        payload="points",
        provider_token="",
        currency="XTR",
        prices=prices
    )


@dp.pre_checkout_query()
async def checkout(pre_checkout_query: types.PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)


@dp.message(lambda message: message.successful_payment)
async def success(message: types.Message):

    user_id = message.from_user.id

    if user_id not in user_points:
        user_points[user_id] = 0

    user_points[user_id] += 1000

    await message.answer(f"تم الدفع بنجاح ✅\nرصيدك: {user_points[user_id]} نقطة")


async def main():
    await dp.start_polling(bot)

asyncio.run(main())
