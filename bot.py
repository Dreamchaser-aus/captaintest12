import os
import threading
import asyncio
import psycopg2
from urllib.request import urlopen

from flask import Flask, request, redirect, session, render_template

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters


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
# WEBHOOK CLEAN
# =========================
def clear_webhook():
    if not BOT_TOKEN:
        return
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/deleteWebhook?drop_pending_updates=true"
        resp = urlopen(url, timeout=10)
        print("[WEBHOOK]", resp.read().decode())
    except Exception as e:
        print("[WEBHOOK ERROR]", e)


# =========================
# DB
# =========================
def get_db_connection():
    return psycopg2.connect(DATABASE_URL, sslmode="require")


def init_db():
    conn = get_db_connection()
    cur = conn.cursor()

    # settings
    cur.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
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

    conn.commit()
    cur.close()
    conn.close()


# =========================
# SETTINGS ENGINE
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
        return int(get_setting(key) or 0)
    except:
        return 0


# =========================
# USERS SYSTEM
# =========================
def ensure_user(uid, username):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT 1 FROM users WHERE telegram_id=%s", (uid,))
    if not cur.fetchone():
        cur.execute(
            "INSERT INTO users (telegram_id, username) VALUES (%s,%s)",
            (uid, username)
        )
        print("[USER INSERT]", uid)

    conn.commit()
    cur.close()
    conn.close()


# =========================
# MALAYSIA TIME FIXED
# =========================
def get_today_count():
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT COUNT(*)
        FROM users
        WHERE first_seen >= (DATE_TRUNC('day', NOW() AT TIME ZONE 'Asia/Kuala_Lumpur') AT TIME ZONE 'Asia/Kuala_Lumpur')
          AND first_seen <  ((DATE_TRUNC('day', NOW() AT TIME ZONE 'Asia/Kuala_Lumpur') + INTERVAL '1 day') AT TIME ZONE 'Asia/Kuala_Lumpur')
    """)

    c = cur.fetchone()[0]
    cur.close()
    conn.close()
    return c


def get_month_count():
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT COUNT(*)
        FROM users
        WHERE first_seen >= (DATE_TRUNC('month', NOW() AT TIME ZONE 'Asia/Kuala_Lumpur') AT TIME ZONE 'Asia/Kuala_Lumpur')
          AND first_seen <  ((DATE_TRUNC('month', NOW() AT TIME ZONE 'Asia/Kuala_Lumpur') + INTERVAL '1 month') AT TIME ZONE 'Asia/Kuala_Lumpur')
    """)

    c = cur.fetchone()[0]
    cur.close()
    conn.close()
    return c


# =========================
# BOT
# =========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    ensure_user(user.id, user.username or user.first_name)

    today = get_today_count() + get_int_setting("manual_today")
    month = get_month_count() + get_int_setting("manual_month")

    text = get_setting("welcome_text").format(
        username=user.first_name,
        user_id=user.id,
        today=today,
        month=month
    )

    await update.message.reply_text(text)


# =========================
# BOT RUN
# =========================
def run_bot():
    async def main():
        app = Application.builder().token(BOT_TOKEN).build()

        app.add_handler(CommandHandler("start", start))

        print("[BOT] running...")
        await app.initialize()
        await app.start()
        await app.updater.start_polling()

        await asyncio.Event().wait()

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(main())


# =========================
# START SYSTEM
# =========================
init_db()
clear_webhook()

if os.getenv("RUN_MAIN") != "true":
    t = threading.Thread(target=run_bot, daemon=True)
    t.start()


@flask_app.route("/")
def home():
    return "OK"


if __name__ == "__main__":
    flask_app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
