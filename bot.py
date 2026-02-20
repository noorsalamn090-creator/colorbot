import telebot
import sqlite3
import os
from telebot.types import ReplyKeyboardMarkup, KeyboardButton

TOKEN = os.getenv("TOKEN")

bot = telebot.TeleBot(TOKEN)

conn = sqlite3.connect("db.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    points INTEGER DEFAULT 0,
    invited_by INTEGER
)
""")
conn.commit()


def menu():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("⭐ نقاطي", "👥 رابط الدعوة")
    markup.row("🎁 الهدية اليومية", "ℹ️ معلوماتي")
    return markup


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

        cursor.execute(
            "INSERT INTO users VALUES (?, ?, ?)",
            (user_id, 0, invited_by)
        )

        conn.commit()

    cursor.execute("SELECT points FROM users WHERE user_id=?", (user_id,))
    points = cursor.fetchone()[0]

    link = f"https://t.me/{bot.get_me().username}?start={user_id}"

    bot.send_message(
        user_id,
        f"اهلا بك\n\n⭐ نقاطك: {points}\n\nرابط الدعوة:\n{link}",
        reply_markup=menu()
    )


@bot.message_handler(func=lambda m: m.text == "⭐ نقاطي")
def points(message):

    cursor.execute(
        "SELECT points FROM users WHERE user_id=?",
        (message.from_user.id,)
    )

    points = cursor.fetchone()[0]

    bot.send_message(
        message.chat.id,
        f"⭐ نقاطك: {points}"
    )


@bot.message_handler(func=lambda m: m.text == "👥 رابط الدعوة")
def invite(message):

    user_id = message.from_user.id

    link = f"https://t.me/{bot.get_me().username}?start={user_id}"

    bot.send_message(
        message.chat.id,
        link
    )


@bot.message_handler(func=lambda m: m.text == "🎁 الهدية اليومية")
def gift(message):

    cursor.execute(
        "UPDATE users SET points = points + 5 WHERE user_id=?",
        (message.from_user.id,)
    )

    conn.commit()

    bot.send_message(
        message.chat.id,
        "تم اضافة 5 نقاط"
    )


@bot.message_handler(func=lambda m: m.text == "ℹ️ معلوماتي")
def info(message):

    user_id = message.from_user.id

    cursor.execute(
        "SELECT points FROM users WHERE user_id=?",
        (user_id,)
    )

    points = cursor.fetchone()[0]

    bot.send_message(
        message.chat.id,
        f"ID: {user_id}\nPoints: {points}"
    )


print("Bot running...")

bot.infinity_polling()
