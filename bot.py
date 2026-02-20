 import telebot
import sqlite3
import os
import time
from telebot.types import ReplyKeyboardMarkup

TOKEN = os.getenv("TOKEN")

bot = telebot.TeleBot(TOKEN)

ADMIN_ID = 7052261939
CHANNEL = "@r_3_666"

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


def menu(user_id):
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("👥 دعوة", "⭐ نقاطي")
    kb.add("🎁 هدية يومية", "💰 سحب")
    if user_id == ADMIN_ID:
        kb.add("⚙️ لوحة الادمن")
    return kb


def get_points(user_id):
    cursor.execute("SELECT points FROM users WHERE user_id=?", (user_id,))
    data = cursor.fetchone()
    if data:
        return data[0]
    return 0


@bot.message_handler(commands=['start'])
def start(message):

    user_id = message.from_user.id

    cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    user = cursor.fetchone()

    args = message.text.split()

    if not user:

        invited_by = None

        if len(args) > 1:

            invited_by = int(args[1])

            if invited_by != user_id:

                cursor.execute(
                    "UPDATE users SET points = points + 1 WHERE user_id=?",
                    (invited_by,)
                )

        cursor.execute(
            "INSERT INTO users (user_id, invited_by) VALUES (?,?)",
            (user_id, invited_by)
        )

        conn.commit()

    link = f"https://t.me/{bot.get_me().username}?start={user_id}"

    bot.send_message(
        user_id,
        f"نقاطك: {get_points(user_id)}\nرابطك:\n{link}",
        reply_markup=menu(user_id)
    )


@bot.message_handler(func=lambda m: m.text == "⭐ نقاطي")
def points(message):
    bot.send_message(message.chat.id, str(get_points(message.from_user.id)))


@bot.message_handler(func=lambda m: m.text == "👥 دعوة")
def invite(message):
    link = f"https://t.me/{bot.get_me().username}?start={message.from_user.id}"
    bot.send_message(message.chat.id, link)


@bot.message_handler(func=lambda m: m.text == "🎁 هدية يومية")
def gift(message):

    user_id = message.from_user.id

    cursor.execute("SELECT last_gift FROM users WHERE user_id=?", (user_id,))
    last = cursor.fetchone()[0]

    now = int(time.time())

    if now - last < 86400:
        bot.send_message(user_id, "ارجع بعد 24 ساعة")
        return

    cursor.execute(
        "UPDATE users SET points = points + 5, last_gift=? WHERE user_id=?",
        (now, user_id)
    )

    conn.commit()

    bot.send_message(user_id, "تم إضافة 5 نقاط")


@bot.message_handler(func=lambda m: m.text == "💰 سحب")
def withdraw(message):

    pts = get_points(message.from_user.id)

    if pts < 10:
        bot.send_message(message.chat.id, "الحد الأدنى 10 نقاط")
        return

    bot.send_message(
        ADMIN_ID,
        f"طلب سحب من {message.from_user.id}\nنقاط: {pts}"
    )

    bot.send_message(message.chat.id, "تم إرسال طلبك")


@bot.message_handler(func=lambda m: m.text == "⚙️ لوحة الادمن")
def admin(message):

    if message.from_user.id != ADMIN_ID:
        return

    cursor.execute("SELECT COUNT(*) FROM users")
    count = cursor.fetchone()[0]

    bot.send_message(message.chat.id, f"عدد المستخدمين: {count}")


print("Bot running")

bot.infinity_polling()
