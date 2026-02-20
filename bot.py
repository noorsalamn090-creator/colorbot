 import telebot
import sqlite3
import os
from telebot.types import ReplyKeyboardMarkup

TOKEN = os.getenv("TOKEN")

bot = telebot.TeleBot(TOKEN)

ADMIN_ID = 7052261939  # غيره الى ايديك

# قاعدة البيانات
conn = sqlite3.connect("db.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    points INTEGER DEFAULT 0
)
""")

conn.commit()


# القائمة الرئيسية
def menu():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("📊 نقاطي")
    return markup


# ستارت
@bot.message_handler(commands=['start'])
def start(message):

    user_id = message.from_user.id

    cursor.execute(
        "INSERT OR IGNORE INTO users (user_id, points) VALUES (?,0)",
        (user_id,)
    )

    conn.commit()

    bot.send_message(
        user_id,
        "اهلا بك في البوت",
        reply_markup=menu()
    )


# عرض النقاط
@bot.message_handler(func=lambda m: m.text == "📊 نقاطي")
def my_points(message):

    user_id = message.from_user.id

    cursor.execute(
        "SELECT points FROM users WHERE user_id=?",
        (user_id,)
    )

    points = cursor.fetchone()[0]

    bot.send_message(
        user_id,
        f"نقاطك: {points}"
    )


# لوحة الادمن
def admin_menu():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("➕ اضافة نقاط", "➖ تصفير نقاط")
    markup.row("📊 احصائيات")
    return markup


@bot.message_handler(commands=['admin'])
def admin(message):

    if message.from_user.id != ADMIN_ID:
        return

    bot.send_message(
        message.chat.id,
        "لوحة الادمن",
        reply_markup=admin_menu()
    )


# احصائيات
@bot.message_handler(func=lambda m: m.text == "📊 احصائيات")
def stats(message):

    if message.from_user.id != ADMIN_ID:
        return

    cursor.execute("SELECT COUNT(*) FROM users")

    count = cursor.fetchone()[0]

    bot.send_message(
        message.chat.id,
        f"عدد المستخدمين: {count}"
    )


# اضافة نقاط
@bot.message_handler(func=lambda m: m.text == "➕ اضافة نقاط")
def add_points(message):

    if message.from_user.id != ADMIN_ID:
        return

    msg = bot.send_message(
        message.chat.id,
        "ارسل: ID عدد_النقاط"
    )

    bot.register_next_step_handler(msg, process_add)


def process_add(message):

    try:

        user_id, points = message.text.split()

        cursor.execute(
            "UPDATE users SET points = points + ? WHERE user_id=?",
            (int(points), int(user_id))
        )

        conn.commit()

        bot.send_message(
            message.chat.id,
            "تمت الاضافة"
        )

    except:

        bot.send_message(
            message.chat.id,
            "خطأ"
        )


# تصفير نقاط
@bot.message_handler(func=lambda m: m.text == "➖ تصفير نقاط")
def reset_points(message):

    if message.from_user.id != ADMIN_ID:
        return

    msg = bot.send_message(
        message.chat.id,
        "ارسل ID"
    )

    bot.register_next_step_handler(msg, process_reset)


def process_reset(message):

    try:

        user_id = int(message.text)

        cursor.execute(
            "UPDATE users SET points = 0 WHERE user_id=?",
            (user_id,)
        )

        conn.commit()

        bot.send_message(
            message.chat.id,
            "تم التصفير"
        )

    except:

        bot.send_message(
            message.chat.id,
            "خطأ"
        )


print("Bot running...")

bot.infinity_polling()
