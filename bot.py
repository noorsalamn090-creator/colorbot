  import telebot
import sqlite3
import os
from telebot.types import ReplyKeyboardMarkup, KeyboardButton

# التوكن من Railway Variables
TOKEN = os.getenv("TOKEN")

bot = telebot.TeleBot(TOKEN)

# قاعدة البيانات
conn = sqlite3.connect("db.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    points INTEGER DEFAULT 0,
    invited_by INTEGER DEFAULT NULL
)
""")
conn.commit()


# إنشاء الأزرار
def main_buttons():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)

    markup.row(
        KeyboardButton("👥 رابط الدعوة"),
        KeyboardButton("⭐ نقاطي")
    )

    markup.row(
        KeyboardButton("🎁 الهدية اليومية"),
        KeyboardButton("ℹ️ معلوماتي")
    )

    return markup


# أمر start
@bot.message_handler(commands=['start'])
def start(message):

    user_id = message.from_user.id
    args = message.text.split()

    cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    user = cursor.fetchone()

    # مستخدم جديد
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

                try:
                    bot.send_message(
                        invited_by,
                        "🎉 شخص دخل من رابط دعوتك!\n⭐ تم إضافة نقطة"
                    )
                except:
                    pass

        cursor.execute(
            "INSERT INTO users (user_id, points, invited_by) VALUES (?, ?, ?)",
            (user_id, 0, invited_by)
        )

        conn.commit()

    # جلب النقاط
    cursor.execute("SELECT points FROM users WHERE user_id=?", (user_id,))
    points = cursor.fetchone()[0]

    link = f"https://t.me/{bot.get_me().username}?start={user_id}"

    bot.send_message(
        user_id,
        f"""
👋 أهلاً بك في بوت التمويل

⭐ نقاطك: {points}

🔗 رابط الدعوة الخاص بك:
{link}

اجمع نقاط بدعوة أصدقائك
""",
        reply_markup=main_buttons()
    )


# عرض النقاط
@bot.message_handler(func=lambda msg: msg.text == "⭐ نقاطي")
def points(message):

    user_id = message.from_user.id

    cursor.execute("SELECT points FROM users WHERE user_id=?", (user_id,))
    points = cursor.fetchone()[0]

    bot.send_message(
        user_id,
        f"⭐ نقاطك الحالية: {points}"
    )


# رابط الدعوة
@bot.message_handler(func=lambda msg: msg.text == "👥 رابط الدعوة")
def invite(message):

    user_id = message.from_user.id

    link = f"https://t.me/{bot.get_me().username}?start={user_id}"

    bot.send_message(
        user_id,
        f"🔗 رابط دعوتك:\n{link}"
    )


# معلوماتي
@bot.message_handler(func=lambda msg: msg.text == "ℹ️ معلوماتي")
def info(message):

    user_id = message.from_user.id

    cursor.execute("SELECT points FROM users WHERE user_id=?", (user_id,))
    points = cursor.fetchone()[0]

    bot.send_message(
        user_id,
        f"""
🆔 ID: {user_id}
⭐ النقاط: {points}
"""
    )


# الهدية اليومية (تجريبية)
@bot.message_handler(func=lambda msg: msg.text == "🎁 الهدية اليومية")
def gift(message):

    user_id = message.from_user.id

    cursor.execute(
        "UPDATE users SET points = points + 5 WHERE user_id=?",
        (user_id,)
    )

    conn.commit()

    bot.send_message(
        user_id,
        "🎁 تم إضافة 5 نقاط كهدية!"
    )


print("Bot running...")

bot.infinity_polling()
