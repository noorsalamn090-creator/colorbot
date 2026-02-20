import telebot
import sqlite3
import os

TOKEN = os.getenv("TOKEN")

bot = telebot.TeleBot(TOKEN)

# إنشاء قاعدة البيانات
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


# أمر start
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    args = message.text.split()

    # إضافة المستخدم إذا غير موجود
    cursor.execute("SELECT user_id FROM users WHERE user_id=?", (user_id,))
    exists = cursor.fetchone()

    if not exists:

        invited_by = None

        # إذا دخل عن طريق رابط دعوة
        if len(args) > 1:
            invited_by = int(args[1])

            if invited_by != user_id:
                cursor.execute("UPDATE users SET points = points + 1 WHERE user_id=?", (invited_by,))
                conn.commit()

                bot.send_message(invited_by, "🎉 شخص دخل من رابط الدعوة الخاص بك!\n+1 نقطة")

        cursor.execute(
            "INSERT INTO users (user_id, points, invited_by) VALUES (?, 0, ?)",
            (user_id, invited_by)
        )
        conn.commit()

    # إنشاء رابط الدعوة
    link = f"https://t.me/{bot.get_me().username}?start={user_id}"

    bot.send_message(user_id, f"""
👋 أهلا بك في البوت

🔗 رابط الدعوة الخاص بك:
{link}

⭐ نقاطك: {get_points(user_id)}

ارسل الرابط لأصدقائك واحصل على نقاط!
""")


# عرض النقاط
@bot.message_handler(commands=['points'])
def points(message):
    user_id = message.from_user.id
    pts = get_points(user_id)

    bot.send_message(user_id, f"⭐ نقاطك: {pts}")


# دالة جلب النقاط
def get_points(user_id):
    cursor.execute("SELECT points FROM users WHERE user_id=?", (user_id,))
    result = cursor.fetchone()

    if result:
        return result[0]
    return 0


print("Bot running...")

bot.infinity_polling()
