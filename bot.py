import telebot
import sqlite3

TOKEN = "8487673303:AAEcVT2ikv0Av_cxTUGvziqUrDyESuqnVyo"

bot = telebot.TeleBot(TOKEN)

conn = sqlite3.connect("db.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    invited_by INTEGER,
    points INTEGER DEFAULT 0
)
""")
conn.commit()


# تسجيل مستخدم جديد
def add_user(user_id, inviter=None):
    cursor.execute("SELECT user_id FROM users WHERE user_id=?", (user_id,))
    if cursor.fetchone() is None:
        cursor.execute(
            "INSERT INTO users (user_id, invited_by, points) VALUES (?, ?, 0)",
            (user_id, inviter)
        )
        conn.commit()

        # إضافة نقطة للشخص الداعي
        if inviter:
            cursor.execute(
                "UPDATE users SET points = points + 1 WHERE user_id=?",
                (inviter,)
            )
            conn.commit()


# جلب النقاط
def get_points(user_id):
    cursor.execute(
        "SELECT points FROM users WHERE user_id=?",
        (user_id,)
    )
    result = cursor.fetchone()
    return result[0] if result else 0


# أمر start
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id

    args = message.text.split()

    inviter = None

    if len(args) > 1:
        inviter = int(args[1])
        if inviter == user_id:
            inviter = None

    add_user(user_id, inviter)

    link = f"https://t.me/{bot.get_me().username}?start={user_id}"

    points = get_points(user_id)

    text = f"""
👋 اهلاً بك

🔗 رابط الدعوة الخاص بك:
{link}

⭐ نقاطك: {points}

📢 ادعُ اصدقائك لتحصل على نقاط
"""

    bot.send_message(user_id, text)


# عرض النقاط
@bot.message_handler(commands=['points'])
def points(message):
    user_id = message.from_user.id
    pts = get_points(user_id)

    bot.send_message(user_id, f"⭐ نقاطك: {pts}")


# السحب (تجريبي)
@bot.message_handler(commands=['withdraw'])
def withdraw(message):
    user_id = message.from_user.id
    pts = get_points(user_id)

    if pts < 5:
        bot.send_message(user_id, "❌ تحتاج 5 نقاط على الأقل للسحب")
    else:
        bot.send_message(user_id, "✅ تم طلب السحب، سيتم المراجعة")


print("Bot running...")
bot.infinity_polling()
