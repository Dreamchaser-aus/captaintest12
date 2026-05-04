import os
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

BOT_TOKEN = os.getenv("BOT_TOKEN")

MAIN_BANNER = "https://i.imgur.com/4M7IWwP.jpeg"


# =========================
# PROMOTIONS
# =========================
PROMOTIONS = {
    "promo_1": {
        "image": "https://i.imgur.com/5qHnQ0R.jpeg",
        "caption": (
            "🔥 WELCOME BONUS\n\n"
            "Deposit RM50 → Free RM10\n"
            "Fast Withdraw ⚡"
        ),
        "buttons": [
            [InlineKeyboardButton("🚀 Register", url="https://yourwebsite.com")],
            [InlineKeyboardButton("💬 Contact", url="https://t.me/your_support")]
        ]
    },
    "promo_2": {
        "image": "https://i.imgur.com/8zQnF4T.jpeg",
        "caption": (
            "🎁 VIP CASHBACK\n\n"
            "Weekly cashback up to 15%\n"
            "No turnover required"
        ),
        "buttons": [
            [InlineKeyboardButton("🚀 Join", url="https://yourwebsite.com")],
            [InlineKeyboardButton("💬 Support", url="https://t.me/your_support")]
        ]
    },
    "promo_3": {
        "image": "https://i.imgur.com/2gRkPjH.jpeg",
        "caption": (
            "💎 DAILY BONUS\n\n"
            "Daily reward system\n"
            "Fast payout ⚡"
        ),
        "buttons": [
            [InlineKeyboardButton("🚀 Deposit", url="https://yourwebsite.com")],
            [InlineKeyboardButton("💬 Support", url="https://t.me/your_support")]
        ]
    }
}


# =========================
# KEYBOARDS
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
            ["💎 Promo 3"],
            ["⬅️ Back", "❌ Close"],
            ["📌 About", "📞 Contact", "🚀 Register"]
        ],
        resize_keyboard=True
    )


# =========================
# START（只显示一次 user info）
# =========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    username = user.username if user.username else user.first_name
    user_id = user.id

    text = (
        f"👋 Welcome {username}\n"
        f"🆔 Your ID: {user_id}\n\n"
        "Welcome to Promotion Center 🔥\n"
        "Choose action below:"
    )

    keyboard = [
        [
            InlineKeyboardButton("🚀 Register", url="https://yourwebsite.com"),
            InlineKeyboardButton("📋 Menu", callback_data="open_menu")
        ]
    ]

    await update.message.reply_photo(
        photo=MAIN_BANNER,
        caption=text,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# =========================
# SEND PROMO
# =========================
async def send_promo(update: Update, key: str):
    promo = PROMOTIONS[key]

    keyboard = promo["buttons"] + [
        [InlineKeyboardButton("⬅️ Back Menu", callback_data="back_menu")]
    ]

    await update.message.reply_photo(
        photo=promo["image"],
        caption=promo["caption"],
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# =========================
# TEXT HANDLER
# =========================
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message.text.strip()

    if msg == "📋 MENU":
        await update.message.reply_text(
            "🔥 Menu Opened",
            reply_markup=expanded_keyboard()
        )

    elif msg == "❌ Close":
        await update.message.reply_text(
            "Menu Closed",
            reply_markup=base_keyboard()
        )

    elif msg == "⬅️ Back":
        await update.message.reply_text(
            "Back to Menu",
            reply_markup=expanded_keyboard()
        )

    elif msg == "🔥 Promo 1":
        await send_promo(update, "promo_1")

    elif msg == "🎁 Promo 2":
        await send_promo(update, "promo_2")

    elif msg == "💎 Promo 3":
        await send_promo(update, "promo_3")

    elif msg == "📌 About":
        await update.message.reply_text(
            "📌 About Us\n\nFast Withdraw | 24/7 Support"
        )

    elif msg == "📞 Contact":
        keyboard = [
            [InlineKeyboardButton("💬 Telegram", url="https://t.me/your_support")],
            [InlineKeyboardButton("💬 WhatsApp", url="https://wa.me/60139661818")]
        ]
        await update.message.reply_text(
            "📞 Contact Us",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif msg == "🚀 Register":
        keyboard = [
            [InlineKeyboardButton("🌍 Register", url="https://yourwebsite.com")]
        ]
        await update.message.reply_text(
            "🚀 Register Now",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )


# =========================
# CALLBACK HANDLER
# =========================
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


# =========================
# MAIN
# =========================
def main():
    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN not set in environment variables")

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.add_handler(CallbackQueryHandler(button_handler))

    print("Bot running...")
    app.run_polling()


if __name__ == "__main__":
    main()
