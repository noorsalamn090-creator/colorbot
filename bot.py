import telebot
import sqlite3
import os
import time
from telebot.types import ReplyKeyboardMarkup, KeyboardButton

TOKEN = os.getenv("TOKEN")

bot = telebot.TeleBot(TOKEN)

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


# القائمة
def menu():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("⭐ نقاطي", "👥 رابط الدعوة")
    markup.row("🎁 الهدية اليومية", "📊 معلوماتي")
    return markup


# start
@bot.message_handler(commands=['start'])
def start(message):

    user_id = message.from_user.id
    args = message.text.split()

    cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    user = cursor.fetchone()

    if not user:

        invited_by = None

        if len(args) > 1:
            invited_by = int(args[1])

            if invited_by != user_id:

                cursor.execute(
                    "UPDATE users SET points = points + 1 WHERE user_id=?",
                    (invited_by,)
                )

                conn.commit()

                bot.send_message(
                    invited_by,
                    "🎉 تم اضافة نقطة من دعوة شخص"
                )

        cursor.execute(
            "INSERT INTO users (user_id, points, invited_by) VALUES (?, ?, ?)",
            (user_id, 0, invited_by)
        )

        conn.commit()

    cursor.execute(
        "SELECT points FROM users WHERE user_id=?",
        (user_id,)
    )

    points = cursor.fetchone()[0]

    link = f"https://t.me/{bot.get_me().username}?start={user_id}"

    bot.send_message(
        user_id,
        f"""
اهلا بك في بوت التمويل

⭐ نقاطك: {points}

👥 رابط الدعوة:
{link}

ادعُ اصدقاءك واحصل على نقاط
""",
        reply_markup=menu()
    )


# نقاطي
@bot.message_handler(func=lambda m: m.text == "⭐ نقاطي")
def my_points(message):

    cursor.execute(
        "SELECT points FROM users WHERE user_id=?",
        (message.from_user.id,)
    )

    points = cursor.fetchone()[0]

    bot.send_message(
        message.chat.id,
        f"⭐ نقاطك: {points}"
    )


# رابط الدعوة
@bot.message_handler(func=lambda m: m.text == "👥 رابط الدعوة")
def invite(message):

    user_id = message.from_user.id

    link = f"https://t.me/{bot.get_me().username}?start={user_id}"

    bot.send_message(
        message.chat.id,
        f"رابط الدعوة:\n{link}"
    )


# الهدية اليومية
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
            message.chat.id,
            "لقد استلمت الهدية اليوم"
        )

        return

    cursor.execute(
        "UPDATE users SET points = points + 5, last_gift=? WHERE user_id=?",
        (now, user_id)
    )

    conn.commit()

    bot.send_message(
        message.chat.id,
        "🎁 تم اضافة 5 نقاط"
    )


# معلوماتي
@bot.message_handler(func=lambda m: m.text == "📊 معلوماتي")
def info(message):

    user_id = message.from_user.id

    cursor.execute(
        "SELECT points FROM users WHERE user_id=?",
        (user_id,)
    )

    points = cursor.fetchone()[0]

    bot.send_message(
        message.chat.id,
        f"""
ID: {user_id}
Points: {points}
"""
    )


print("Bot running...")

bot.infinity_polling()
