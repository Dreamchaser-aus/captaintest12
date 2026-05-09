import os
import threading
import asyncio
import psycopg2

from urllib.request import urlopen

from flask import Flask, render_template, request, redirect, session

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup
)
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)

# =========================
# CONST
# =========================
BOT_TOKEN = os.getenv("BOT_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL")

ADMIN_USER = os.getenv("ADMIN_USER", "admin")
ADMIN_PASS = os.getenv("ADMIN_PASS", "admin123")
SECRET_KEY = os.getenv("SECRET_KEY", "secret123")

# =========================
# FLASK
# =========================
flask_app = Flask(__name__)
flask_app.secret_key = SECRET_KEY


# =========================
# DB
# =========================
def get_db_connection():
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL not set in Railway Variables")
    return psycopg2.connect(DATABASE_URL, sslmode="require")


def init_db():
    conn = get_db_connection()
    cur = conn.cursor()

    # settings
    cur.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )
    """)

    # users
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            telegram_id BIGINT UNIQUE,
            username TEXT,
            first_seen TIMESTAMPTZ DEFAULT NOW()
        )
    """)

    # 🔥 FIX: registration log (核心修复)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS registration_log (
            id SERIAL PRIMARY KEY,
            telegram_id BIGINT,
            created_at TIMESTAMPTZ DEFAULT NOW()
        )
    """)

    # promos
    cur.execute("""
        CREATE TABLE IF NOT EXISTS promos (
            id SERIAL PRIMARY KEY,
            title TEXT,
            image_url TEXT,
            caption TEXT,
            is_active BOOLEAN DEFAULT TRUE
        )
    """)

    # promo buttons
    cur.execute("""
        CREATE TABLE IF NOT EXISTS promo_buttons (
            id SERIAL PRIMARY KEY,
            promo_id INT,
            text TEXT,
            url TEXT,
            sort_order INT DEFAULT 0
        )
    """)

    # banner buttons
    cur.execute("""
        CREATE TABLE IF NOT EXISTS banner_buttons (
            id SERIAL PRIMARY KEY,
            text TEXT,
            url TEXT,
            callback_data TEXT,
            sort_order INT DEFAULT 0
        )
    """)

    # default settings
    defaults = {
        "main_banner": "https://i.imgur.com/4M7IWwP.jpeg",
        "welcome_text": "👋 Welcome {username}\n🆔 {user_id}\n📅 Today: {today_count}\n🗓 Month: {month_count}",
        "about_text": "Fast Withdraw | 24/7 Support",
        "register_url": "https://yourwebsite.com",
        "telegram_support": "https://t.me/your_support",
        "whatsapp_url": "https://wa.me/60139661818",
        "manual_today_add": "0",
        "manual_month_add": "0"
    }

    for k, v in defaults.items():
        cur.execute("""
            INSERT INTO settings (key, value)
            VALUES (%s, %s)
            ON CONFLICT (key) DO NOTHING
        """, (k, v))

    conn.commit()
    cur.close()
    conn.close()


# =========================
# SETTINGS
# =========================
def get_setting(key):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT value FROM settings WHERE key=%s", (key,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    return row[0] if row else ""


def set_setting(key, value):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO settings (key,value)
        VALUES (%s,%s)
        ON CONFLICT (key) DO UPDATE SET value=EXCLUDED.value
    """, (key, value))
    conn.commit()
    cur.close()
    conn.close()


def get_int_setting(key):
    try:
        return int(get_setting(key))
    except:
        return 0


# =========================
# USER REGISTER + LOG
# =========================
def ensure_user(user_id, username):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT telegram_id FROM users WHERE telegram_id=%s", (user_id,))
    row = cur.fetchone()

    if not row:
        cur.execute("""
            INSERT INTO users (telegram_id, username)
            VALUES (%s,%s)
        """, (user_id, username))

        # 🔥 log event
        cur.execute("""
            INSERT INTO registration_log (telegram_id)
            VALUES (%s)
        """, (user_id,))

    conn.commit()
    cur.close()
    conn.close()


# =========================
# TIME FIX (GMT+8 CORRECT)
# =========================
def get_today_count():
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT COUNT(*)
        FROM registration_log
        WHERE (created_at AT TIME ZONE 'Asia/Kuala_Lumpur')::date
        =
        (NOW() AT TIME ZONE 'Asia/Kuala_Lumpur')::date
    """)

    count = cur.fetchone()[0]
    cur.close()
    conn.close()
    return count


def get_month_count():
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT COUNT(*)
        FROM registration_log
        WHERE DATE_TRUNC('month', created_at AT TIME ZONE 'Asia/Kuala_Lumpur')
        =
        DATE_TRUNC('month', NOW() AT TIME ZONE 'Asia/Kuala_Lumpur')
    """)

    count = cur.fetchone()[0]
    cur.close()
    conn.close()
    return count


# =========================
# START
# =========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    username = user.username or user.first_name
    user_id = user.id

    ensure_user(user_id, username)

    today = get_today_count() + get_int_setting("manual_today_add")
    month = get_month_count() + get_int_setting("manual_month_add")

    text = get_setting("welcome_text")
    text = text.replace("{username}", username)
    text = text.replace("{user_id}", str(user_id))
    text = text.replace("{today_count}", str(today))
    text = text.replace("{month_count}", str(month))

    keyboard = [
        [InlineKeyboardButton("🚀 Register", url=get_setting("register_url"))],
        [InlineKeyboardButton("📋 Menu", callback_data="menu")]
    ]

    await update.message.reply_photo(
        photo=get_setting("main_banner"),
        caption=text,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# =========================
# BOT CORE
# =========================
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Menu System Active")


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    if q.data == "menu":
        await q.message.reply_text("Menu Opened")


# =========================
# WEBHOOK FIX + BOT RUN
# =========================
def clear_webhook():
    if not BOT_TOKEN:
        print("BOT_TOKEN missing, cannot clear webhook")
        return

    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/deleteWebhook?drop_pending_updates=true"
        resp = urlopen(url, timeout=10)
        print("Webhook cleared:", resp.read().decode("utf-8"))
    except Exception as e:
        print("Webhook clear failed:", e)


def run_bot():
    async def main():
        clear_webhook()

        app = Application.builder().token(BOT_TOKEN).build()

        app.add_handler(CommandHandler("start", start))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
        app.add_handler(CallbackQueryHandler(button_handler))

        await app.initialize()
        await app.start()
        await app.updater.start_polling()

        await asyncio.Event().wait()

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(main())


# =========================
# FLASK THREAD
# =========================
def flask_run():
    flask_app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))


# =========================
# MAIN
# =========================
init_db()

threading.Thread(target=run_bot, daemon=True).start()
threading.Thread(target=flask_run, daemon=True).start()

print("System Running...")
