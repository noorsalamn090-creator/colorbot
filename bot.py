import os
import telebot
import sqlite3
from telebot.types import ReplyKeyboardMarkup

TOKEN = os.getenv("TOKEN")
CHANNEL = "@r_3_666"  # ضع معرف قناتك
ADMIN_ID = 7052261939  # ضع ايديك

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

def is_joined(user_id):
    try:
        member = bot.get_chat_member(CHANNEL, user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False

def menu():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("📊 نقاطي", "🔗 رابط الدعوة")
    markup.add("💰 سحب النقاط")
    return markup

@bot.message_handler(commands=["start"])
def start(message):
    user_id = message.from_user.id
    args = message.text.split()

    if not is_joined(user_id):
        bot.send_message(user_id, f"اشترك بالقناة أولاً:\n{CHANNEL}")
        return

    cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    user = cursor.fetchone()

    if not user:
        invited_by = None
        if len(args) > 1:
            invited_by = int(args[1])
            cursor.execute("UPDATE users SET points = points + 1 WHERE user_id=?", (invited_by,))
        cursor.execute("INSERT INTO users (user_id, invited_by) VALUES (?, ?)", (user_id, invited_by))
        conn.commit()

    bot.send_message(user_id, "اهلاً بك", reply_markup=menu())

@bot.message_handler(func=lambda m: m.text == "📊 نقاطي")
def points(message):
    cursor.execute("SELECT points FROM users WHERE user_id=?", (message.from_user.id,))
    points = cursor.fetchone()[0]
    bot.send_message(message.from_user.id, f"نقاطك: {points}")

@bot.message_handler(func=lambda m: m.text == "🔗 رابط الدعوة")
def invite(message):
    link = f"https://t.me/{bot.get_me().username}?start={message.from_user.id}"
    bot.send_message(message.from_user.id, link)

@bot.message_handler(func=lambda m: m.text == "💰 سحب النقاط")
def withdraw(message):
    cursor.execute("SELECT points FROM users WHERE user_id=?", (message.from_user.id,))
    points = cursor.fetchone()[0]

    if points < 10:
        bot.send_message(message.from_user.id, "الحد الأدنى للسحب 10 نقاط")
    else:
        bot.send_message(message.from_user.id, "تم إرسال طلبك")
        bot.send_message(ADMIN_ID, f"طلب سحب من {message.from_user.id}")

bot.infinity_polling()
