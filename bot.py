import telebot
import sqlite3
import os
import time
from telebot.types import ReplyKeyboardMarkup, KeyboardButton

TOKEN = os.getenv("TOKEN")

bot = telebot.TeleBot(TOKEN)

ADMIN_ID = 7052261939  # ضع ايديك
CHANNEL = "@r_3_666"  # ضع معرف القناة

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


# تحقق الاشتراك
def check_sub(user_id):

    try:

        member = bot.get_chat_member(CHANNEL, user_id)

        if member.status in ["member", "creator", "administrator"]:
            return True

        else:
            return False

    except:
        return False


# القائمة
def menu(user_id):

    kb = ReplyKeyboardMarkup(resize_keyboard=True)

    kb.add("👥 دعوة", "⭐ نقاطي")

    kb.add("🎁 هدية يومية", "💸 تحويل")

    kb.add("💰 سحب", "📊 حسابي")

    if user_id == ADMIN_ID:
        kb.add("⚙️ لوحة الأدمن")

    return kb


# نقاط
def get_points(user_id):

    cursor.execute(
        "SELECT points FROM users WHERE user_id=?",
        (user_id,)
    )

    data = cursor.fetchone()

    if data:
        return data[0]

    return 0


# start
@bot.message_handler(commands=['start'])
def start(message):

    user_id = message.from_user.id

    if not check_sub(user_id):

        bot.send_message(
            user_id,
            f"اشترك بالقناة أولاً:\n{CHANNEL}"
        )

        return

    args = message.text.split()

    cursor.execute(
        "SELECT user_id FROM users WHERE user_id=?",
        (user_id,)
    )

    exists = cursor.fetchone()

    if not exists:

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
        f"""
أهلاً بك

نقاطك: {get_points(user_id)}

رابط الدعوة:
{link}
        """,
        reply_markup=menu(user_id)
    )


# نقاطي
@bot.message_handler(func=lambda m: m.text == "⭐ نقاطي")
def points(message):

    bot.send_message(
        message.chat.id,
        f"نقاطك: {get_points(message.from_user.id)}"
    )


# دعوة
@bot.message_handler(func=lambda m: m.text == "👥 دعوة")
def invite(message):

    user_id = message.from_user.id

    link = f"https://t.me/{bot.get_me().username}?start={user_id}"

    bot.send_message(
        user_id,
        link
    )


# هدية
@bot.message_handler(func=lambda m: m.text == "🎁 هدية يومية")
def gift(message):

    user_id = message.from_user.id

    cursor.execute(
        "SELECT last_gift FROM users WHERE user_id=?",
        (user_id,)
    )

    last = cursor.fetchone()[0]

    now = int(time.time())

    if now - last < 86400:

        bot.send_message(user_id, "انتظر 24 ساعة")

        return

    cursor.execute(
        "UPDATE users SET points = points + 5, last_gift=? WHERE user_id=?",
        (now, user_id)
    )

    conn.commit()

    bot.send_message(user_id, "تم إضافة 5 نقاط")


# تحويل
@bot.message_handler(func=lambda m: m.text == "💸 تحويل")
def transfer(message):

    bot.send_message(message.chat.id, "ارسل ID")

    bot.register_next_step_handler(
        message,
        transfer2
    )


def transfer2(message):

    receiver = int(message.text)

    bot.send_message(message.chat.id, "كم نقطة")

    bot.register_next_step_handler(
        message,
        lambda m: transfer3(m, receiver)
    )


def transfer3(message, receiver):

    sender = message.from_user.id

    amount = int(message.text)

    if get_points(sender) < amount:

        bot.send_message(sender, "نقاطك غير كافية")

        return

    cursor.execute(
        "UPDATE users SET points=points-? WHERE user_id=?",
        (amount, sender)
    )

    cursor.execute(
        "UPDATE users SET points=points+? WHERE user_id=?",
        (amount, receiver)
    )

    conn.commit()

    bot.send_message(sender, "تم التحويل")


# سحب
@bot.message_handler(func=lambda m: m.text == "💰 سحب")
def withdraw(message):

    user_id = message.from_user.id

    pts = get_points(user_id)

    if pts < 10:

        bot.send_message(user_id, "الحد الأدنى للسحب 10")

        return

    bot.send_message(
        ADMIN_ID,
        f"طلب سحب من {user_id}\nنقاط: {pts}"
    )

    bot.send_message(user_id, "تم إرسال الطلب")


# لوحة الأدمن
@bot.message_handler(func=lambda m: m.text == "⚙️ لوحة الأدمن")
def admin(message):

    if message.from_user.id != ADMIN_ID:
        return

    kb = ReplyKeyboardMarkup(resize_keyboard=True)

    kb.add("➕ إضافة نقاط", "➖ خصم نقاط")

    kb.add("📢 إذاعة")

    bot.send_message(
        ADMIN_ID,
        "لوحة الأدمن",
        reply_markup=kb
    )


# إضافة نقاط
@bot.message_handler(func=lambda m: m.text == "➕ إضافة نقاط")
def add_points(message):

    if message.from_user.id != ADMIN_ID:
        return

    bot.send_message(ADMIN_ID, "ارسل ID")

    bot.register_next_step_handler(
        message,
        add_points2
    )


def add_points2(message):

    user = int(message.text)

    bot.send_message(ADMIN_ID, "كم نقطة")

    bot.register_next_step_handler(
        message,
        lambda m: add_points3(m, user)
    )


def add_points3(message, user):

    amount = int(message.text)

    cursor.execute(
        "UPDATE users SET points=points+? WHERE user_id=?",
        (amount, user)
    )

    conn.commit()

    bot.send_message(ADMIN_ID, "تم")


# تشغيل
print("Running")

bot.infinity_polling()
