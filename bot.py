import telebot
import sqlite3

TOKEN = "8487673303:AAEcVT2ikv0Av_cxTUGvziqUrDyESuqnVyo"

bot = telebot.TeleBot(TOKEN)

conn = sqlite3.connect("db.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, points INTEGER)")
conn.commit()

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id

    cursor.execute("INSERT OR IGNORE INTO users (user_id, points) VALUES (?, 0)", (user_id,))
    conn.commit()

    link = f"https://t.me/{bot.get_me().username}?start={user_id}"

    bot.send_message(user_id, f"اهلا بك\nرابط الدعوة:\n{link}")

bot.infinity_polling()
