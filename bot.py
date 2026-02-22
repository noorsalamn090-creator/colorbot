import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, LabeledPrice
from aiogram.filters import Command

# حط توكن بوتك هنا
TOKEN = "8555686519:AAGb-AiAYSgm0_mONFr5Hnwg0GfPiRpXyvM"

bot = Bot(token=TOKEN)
dp = Dispatcher()

# تخزين نقاط المستخدمين
user_points = {}

# المنتجات
products = {
    "buy_1k": {"points": 1000, "price": 1},
    "buy_10k": {"points": 10000, "price": 8},
    "buy_50k": {"points": 50000, "price": 40},
    "buy_100k": {"points": 100000, "price": 75},
    "buy_250k": {"points": 250000, "price": 180},
}

# رسالة start
@dp.message(Command("start"))
async def start(message: types.Message):

    if message.from_user.id not in user_points:
        user_points[message.from_user.id] = 0

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="⭐ شحن 1000 نقطة - 1 نجمة", callback_data="buy_1k")],
            [InlineKeyboardButton(text="⭐ شحن 10000 نقطة - 8 نجوم", callback_data="buy_10k")],
            [InlineKeyboardButton(text="⭐ شحن 50000 نقطة - 40 نجمة", callback_data="buy_50k")],
            [InlineKeyboardButton(text="⭐ شحن 100000 نقطة - 75 نجمة", callback_data="buy_100k")],
            [InlineKeyboardButton(text="⭐ شحن 250000 نقطة - 180 نجمة", callback_data="buy_250k")],
        ]
    )

    await message.answer(
        f"اهلا بك 👋\n\nرصيدك الحالي: {user_points[message.from_user.id]} نقطة\n\nاختر الكمية للشحن:",
        reply_markup=keyboard
    )

# عند الضغط على زر شراء
@dp.callback_query(F.data.startswith("buy_"))
async def buy(callback: types.CallbackQuery):

    product = products[callback.data]

    prices = [
        LabeledPrice(
            label=f"{product['points']} نقطة",
            amount=product['price']
        )
    ]

    await bot.send_invoice(
        chat_id=callback.from_user.id,
        title="شراء نقاط",
        description=f"شراء {product['points']} نقطة",
        payload=callback.data,
        provider_token="",
        currency="XTR",
        prices=prices,
    )

# تأكيد الدفع
@dp.pre_checkout_query()
async def pre_checkout(pre_checkout_query: types.PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

# بعد نجاح الدفع
@dp.message(F.successful_payment)
async def success(message: types.Message):

    payload = message.successful_payment.invoice_payload
    product = products[payload]

    user_points[message.from_user.id] += product["points"]

    await message.answer(
        f"✅ تم الدفع بنجاح!\n\n"
        f"تم إضافة {product['points']} نقطة\n"
        f"رصيدك الجديد: {user_points[message.from_user.id]} نقطة"
    )

# تشغيل البوت
async def main():
    print("Bot is running...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
