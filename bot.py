 import telebot
import sqlite3
import os

TOKEN = os.getenv("TOKEN")
ADMIN_ID = 7052261939
CHANNEL = "@r_3_666l"

bot = telebot.TeleBot(TOKEN)

conn = sqlite3.connect("db.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
user_id INTEGER PRIMARY KEY,
points INTEGER DEFAULT 0,
invited_by INTEGER DEFAULT 0
)
""")
conn.commit()


def get_points(user_id):
    cursor.execute("SELECT points FROM users WHERE user_id=?", (user_id,))
    result = cursor.fetchone()
    if result:
        return result[0]
    return 0


@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id

    cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    exists = cursor.fetchone()

    if not exists:
        invited_by = 0
        args = message.text.split()

        if len(args) > 1:
            invited_by = int(args[1])

            if invited_by != user_id:
                cursor.execute("UPDATE users SET points = points + 1 WHERE user_id=?", (invited_by,))
                conn.commit()
                bot.send_message(invited_by, "🎉 تم دخول شخص من رابط دعوتك")

        cursor.execute("INSERT INTO users (user_id, points, invited_by) VALUES (?, ?, ?)",
                       (user_id, 0, invited_by))
        conn.commit()

    points = get_points(user_id)

    link = f"https://t.me/{bot.get_me().username}?start={user_id}"

    text = f"""
👋 مرحباً بك

⭐ نقاطك: {points}

🔗 رابط الدعوة:
{link}

📋 الأوامر:
/start
/my
"""

    bot.send_message(user_id, text)


@bot.message_handler(commands=['my'])
def my(message):
    user_id = message.from_user.id
    points = get_points(user_id)
    bot.send_message(user_id, f"⭐ نقاطك: {points}")


@bot.message_handler(commands=['admin'])
def admin(message):
    if message.from_user.id != ADMIN_ID:
        return

    cursor.execute("SELECT COUNT(*) FROM users")
    users = cursor.fetchone()[0]

    text = f"""
👨‍💻 لوحة الادمن

عدد المستخدمين: {users}
"""

    bot.send_message(message.chat.id, text)


print("Bot running...")
bot.infinity_polling()
