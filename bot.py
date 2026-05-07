import os
import json
import threading
import psycopg2
from flask import Flask, render_template, request, redirect, session, url_for

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
# ENV SETTINGS
# =========================
BOT_TOKEN = os.getenv("BOT_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL")

ADMIN_USER = os.getenv("ADMIN_USER", "admin")
ADMIN_PASS = os.getenv("ADMIN_PASS", "admin123")

# =========================
# FLASK APP
# =========================
flask_app = Flask(__name__)
flask_app.secret_key = os.getenv("SECRET_KEY", "supersecretkey123")


# =========================
# DATABASE FUNCTIONS
# =========================
def get_db_connection():
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL not found. Please set Railway PostgreSQL DATABASE_URL in Variables.")
    return psycopg2.connect(DATABASE_URL, sslmode="require")


def init_db():
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )
    """)

    conn.commit()

    # default values insert
    default_settings = {
        "main_banner": "https://i.imgur.com/4M7IWwP.jpeg",
        "about_text": "📌 About Us\n\nFast Withdraw | 24/7 Support",
        "register_url": "https://yourwebsite.com",
        "telegram_support": "https://t.me/your_support",
        "whatsapp_url": "https://wa.me/60139661818",
        "promo_1": json.dumps({
            "image": "https://i.imgur.com/5qHnQ0R.jpeg",
            "caption": "🔥 WELCOME BONUS\n\nDeposit RM50 → Free RM10\nFast Withdraw ⚡",
            "button1_text": "🚀 Register",
            "button1_url": "https://yourwebsite.com",
            "button2_text": "💬 Contact",
            "button2_url": "https://t.me/your_support"
        }),
        "promo_2": json.dumps({
            "image": "https://i.imgur.com/8zQnF4T.jpeg",
            "caption": "🎁 VIP CASHBACK\n\nWeekly cashback up to 15%\nNo turnover required",
            "button1_text": "🚀 Join",
            "button1_url": "https://yourwebsite.com",
            "button2_text": "💬 Support",
            "button2_url": "https://t.me/your_support"
        }),
        "promo_3": json.dumps({
            "image": "https://i.imgur.com/2gRkPjH.jpeg",
            "caption": "💎 DAILY BONUS\n\nDaily reward system\nFast payout ⚡",
            "button1_text": "🚀 Deposit",
            "button1_url": "https://yourwebsite.com",
            "button2_text": "💬 Support",
            "button2_url": "https://t.me/your_support"
        })
    }

    for k, v in default_settings.items():
        cur.execute("SELECT key FROM settings WHERE key=%s", (k,))
        if not cur.fetchone():
            cur.execute("INSERT INTO settings (key, value) VALUES (%s, %s)", (k, v))

    conn.commit()
    cur.close()
    conn.close()


def get_setting(key):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT value FROM settings WHERE key=%s", (key,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    return row[0] if row else None


def set_setting(key, value):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO settings (key, value)
        VALUES (%s, %s)
        ON CONFLICT (key)
        DO UPDATE SET value = EXCLUDED.value
    """, (key, value))
    conn.commit()
    cur.close()
    conn.close()


def load_promotions():
    promos = {}
    for i in range(1, 4):
        raw = get_setting(f"promo_{i}")
        if raw:
            promos[f"promo_{i}"] = json.loads(raw)
    return promos


# =========================
# BOT KEYBOARDS
# =========================
def base_keyboard():
    return ReplyKeyboardMarkup(
        [
            ["📋 MENU", "📌 About"],
            ["📞 Contact", "🚀 Register"]
        ],
        resize_keyboard=True
    )


def expanded_keyboard():
    return ReplyKeyboardMarkup(
        [
            ["🔥 Promo 1", "🎁 Promo 2"],
            ["💎 Promo 3", "📌 About"],
            ["⬅️ Back Menu"],
            ["📞 Contact", "🚀 Register"]
        ],
        resize_keyboard=True
    )


# =========================
# BOT HANDLERS
# =========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    username = user.username if user.username else user.first_name
    user_id = user.id

    MAIN_BANNER = get_setting("main_banner")
    register_url = get_setting("register_url")

    text = (
        f"👋 Welcome {username}\n"
        f"🆔 Your ID: {user_id}\n\n"
        "Welcome to Promotion Center 🔥\n"
        "Choose action below:"
    )

    keyboard = [
        [
            InlineKeyboardButton("🚀 Register", url=register_url),
            InlineKeyboardButton("📋 Menu", callback_data="open_menu")
        ]
    ]

    await update.message.reply_photo(
        photo=MAIN_BANNER,
        caption=text,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def send_promo(update: Update, key: str):
    promos = load_promotions()
    promo = promos.get(key)

    if not promo:
        await update.message.reply_text("Promo not found.")
        return

    keyboard = [
        [InlineKeyboardButton(promo["button1_text"], url=promo["button1_url"])],
        [InlineKeyboardButton(promo["button2_text"], url=promo["button2_url"])],
        [InlineKeyboardButton("⬅️ Back Menu", callback_data="back_menu")]
    ]

    await update.message.reply_photo(
        photo=promo["image"],
        caption=promo["caption"],
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message.text.strip()

    if msg == "📋 MENU":
        await update.message.reply_text(
            "🔥 Menu Opened",
            reply_markup=expanded_keyboard()
        )

    elif msg == "⬅️ Back Menu":
        await update.message.reply_text(
            "Menu Closed",
            reply_markup=base_keyboard()
        )

    elif msg == "🔥 Promo 1":
        await send_promo(update, "promo_1")

    elif msg == "🎁 Promo 2":
        await send_promo(update, "promo_2")

    elif msg == "💎 Promo 3":
        await send_promo(update, "promo_3")

    elif msg == "📌 About":
        about_text = get_setting("about_text")
        await update.message.reply_text(about_text)

    elif msg == "📞 Contact":
        telegram_support = get_setting("telegram_support")
        whatsapp_url = get_setting("whatsapp_url")

        keyboard = [
            [InlineKeyboardButton("💬 Telegram", url=telegram_support)],
            [InlineKeyboardButton("💬 WhatsApp", url=whatsapp_url)]
        ]

        await update.message.reply_text(
            "📞 Contact Us",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif msg == "🚀 Register":
        register_url = get_setting("register_url")
        keyboard = [[InlineKeyboardButton("🌍 Register", url=register_url)]]

        await update.message.reply_text(
            "🚀 Register Now",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "open_menu":
        await query.message.reply_text(
            "🔥 Promotion Menu",
            reply_markup=expanded_keyboard()
        )

    elif query.data == "back_menu":
        await query.message.reply_text(
            "Back to Menu",
            reply_markup=expanded_keyboard()
        )


def run_bot():
    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN not set")

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.add_handler(CallbackQueryHandler(button_handler))

    print("Bot running...")
    app.run_polling()


# =========================
# FLASK ADMIN ROUTES
# =========================
@flask_app.route("/")
def home():
    return redirect("/admin")


@flask_app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if username == ADMIN_USER and password == ADMIN_PASS:
            session["admin_logged_in"] = True
            return redirect("/admin")

        return render_template("login.html", error="Invalid username or password")

    return render_template("login.html")


@flask_app.route("/admin/logout")
def admin_logout():
    session.clear()
    return redirect("/admin/login")


@flask_app.route("/admin", methods=["GET", "POST"])
def admin_dashboard():
    if not session.get("admin_logged_in"):
        return redirect("/admin/login")

    if request.method == "POST":
        set_setting("main_banner", request.form.get("main_banner"))
        set_setting("about_text", request.form.get("about_text"))
        set_setting("register_url", request.form.get("register_url"))
        set_setting("telegram_support", request.form.get("telegram_support"))
        set_setting("whatsapp_url", request.form.get("whatsapp_url"))

        for i in range(1, 4):
            promo_data = {
                "image": request.form.get(f"promo_{i}_image"),
                "caption": request.form.get(f"promo_{i}_caption"),
                "button1_text": request.form.get(f"promo_{i}_btn1_text"),
                "button1_url": request.form.get(f"promo_{i}_btn1_url"),
                "button2_text": request.form.get(f"promo_{i}_btn2_text"),
                "button2_url": request.form.get(f"promo_{i}_btn2_url"),
            }
            set_setting(f"promo_{i}", json.dumps(promo_data))

        return redirect("/admin")

    promos = load_promotions()

    data = {
        "main_banner": get_setting("main_banner"),
        "about_text": get_setting("about_text"),
        "register_url": get_setting("register_url"),
        "telegram_support": get_setting("telegram_support"),
        "whatsapp_url": get_setting("whatsapp_url"),
        "promo_1": promos.get("promo_1", {}),
        "promo_2": promos.get("promo_2", {}),
        "promo_3": promos.get("promo_3", {}),
    }

    return render_template("dashboard.html", data=data)


# =========================
# AUTO INIT + RUN BOT THREAD
# =========================
init_db()

bot_thread = threading.Thread(target=run_bot, daemon=True)
bot_thread.start()


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    flask_app.run(host="0.0.0.0", port=port)
