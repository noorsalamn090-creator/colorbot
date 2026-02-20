import telebot
import sqlite3
import os
import time
from telebot.types import ReplyKeyboardMarkup, KeyboardButton

TOKEN = os.getenv("TOKEN")

bot = telebot.TeleBot(TOKEN)

ADMIN_ID =  7052261939 # ضع ايديك هنا

# قاعدة البيانات
conn = sqlite3.connect("db.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    points INTEGER DEFAULT 0,
    invited_by INTEGER,
    last_gift INTEGER DEFAULT 0
)
""")

conn.commit()


# الكيبورد
def main_menu():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)

    kb.add(
        KeyboardButton("👥 دعوة أصدقاء"),
        KeyboardButton("⭐ نقاطي")
    )

    kb.add(
        KeyboardButton("🎁 الهدية اليومية"),
        KeyboardButton("💸 تحويل نقاط")
    )

    kb.add(
        KeyboardButton("📊 حسابي"),
        KeyboardButton("ℹ️ معلومات")
    )

    return kb


# جلب النقاط
def get_points(user_id):

    cursor.execute(
        "SELECT points FROM users WHERE user_id=?",
        (user_id,)
    )

    data = cursor.fetchone()

    if data:
        return data[0]

    return 0


# start
@bot.message_handler(commands=['start'])
def start(message):

    user_id = message.from_user.id

    args = message.text.split()

    cursor.execute(
        "SELECT user_id FROM users WHERE user_id=?",
        (user_id,)
    )

    exists = cursor.fetchone()

    if not exists:

        invited_by = None

        if len(args) > 1:

            invited_by = int(args[1])

            if invited_by != user_id:

                cursor.execute(
                    "UPDATE users SET points = points + 1 WHERE user_id=?",
                    (invited_by,)
                )

                bot.send_message(
                    invited_by,
                    "🎉 تمت إضافة نقطة جديدة من رابط الدعوة!"
                )

        cursor.execute(
            "INSERT INTO users (user_id, points, invited_by) VALUES (?,0,?)",
            (user_id, invited_by)
        )

        conn.commit()

    link = f"https://t.me/{bot.get_me().username}?start={user_id}"

    bot.send_message(
        user_id,
        f"""
🔥 أهلاً بك في بوت التمويل

🆔 ID: {user_id}

⭐ نقاطك: {get_points(user_id)}

🔗 رابط الدعوة:
{link}

ارسل الرابط واحصل على نقاط
        """,
        reply_markup=main_menu()
    )


# نقاطي
@bot.message_handler(func=lambda m: m.text == "⭐ نقاطي")
def points(message):

    pts = get_points(message.from_user.id)

    bot.send_message(
        message.chat.id,
        f"⭐ نقاطك: {pts}"
    )


# دعوة
@bot.message_handler(func=lambda m: m.text == "👥 دعوة أصدقاء")
def invite(message):

    user_id = message.from_user.id

    link = f"https://t.me/{bot.get_me().username}?start={user_id}"

    bot.send_message(
        message.chat.id,
        f"🔗 رابط الدعوة:\n{link}"
    )


# هدية يومية
@bot.message_handler(func=lambda m: m.text == "🎁 الهدية اليومية")
def gift(message):

    user_id = message.from_user.id

    cursor.execute(
        "SELECT last_gift FROM users WHERE user_id=?",
        (user_id,)
    )

    last = cursor.fetchone()[0]

    now = int(time.time())

    if now - last < 86400:

        bot.send_message(
            user_id,
            "⏳ يمكنك الحصول على الهدية مرة كل 24 ساعة"
        )

        return

    cursor.execute(
        "UPDATE users SET points = points + 5, last_gift=? WHERE user_id=?",
        (now, user_id)
    )

    conn.commit()

    bot.send_message(
        user_id,
        "🎁 حصلت على 5 نقاط!"
    )


# تحويل نقاط
@bot.message_handler(func=lambda m: m.text == "💸 تحويل نقاط")
def transfer_start(message):

    bot.send_message(
        message.chat.id,
        "ارسل ID المستخدم:"
    )

    bot.register_next_step_handler(
        message,
        get_transfer_id
    )


def get_transfer_id(message):

    receiver = int(message.text)

    bot.send_message(
        message.chat.id,
        "كم عدد النقاط؟"
    )

    bot.register_next_step_handler(
        message,
        lambda m: do_transfer(m, receiver)
    )


def do_transfer(message, receiver):

    sender = message.from_user.id

    amount = int(message.text)

    if get_points(sender) < amount:

        bot.send_message(
            sender,
            "❌ نقاطك غير كافية"
        )

        return

    cursor.execute(
        "UPDATE users SET points = points - ? WHERE user_id=?",
        (amount, sender)
    )

    cursor.execute(
        "UPDATE users SET points = points + ? WHERE user_id=?",
        (amount, receiver)
    )

    conn.commit()

    bot.send_message(
        sender,
        "✅ تم التحويل"
    )

    bot.send_message(
        receiver,
        f"🎁 تم استلام {amount} نقطة"
    )


# حسابي
@bot.message_handler(func=lambda m: m.text == "📊 حسابي")
def account(message):

    user_id = message.from_user.id

    bot.send_message(
        user_id,
        f"""
🆔 ID: {user_id}
⭐ نقاطك: {get_points(user_id)}
        """
    )


# معلومات
@bot.message_handler(func=lambda m: m.text == "ℹ️ معلومات")
def info(message):

    bot.send_message(
        message.chat.id,
        "بوت تمويل متكامل"
    )


print("Bot running...")

bot.infinity_polling()
