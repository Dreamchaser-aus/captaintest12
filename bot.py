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
# Promotion 数据（可无限扩展）
# =========================
PROMOTIONS = {
    "promo_1": {
        "image": "https://i.imgur.com/5qHnQ0R.jpeg",
        "caption": (
            "🔥 *WELCOME BONUS*\n\n"
            "✅ Deposit RM50 Free RM10\n"
            "✅ Instant Credit\n"
            "✅ Fast Withdraw\n\n"
            "📌 Limited Offer Today"
        ),
        "buttons": [
            [InlineKeyboardButton("🚀 Register", url="https://yourwebsite.com")],
            [InlineKeyboardButton("💬 Contact", url="https://t.me/your_support")]
        ]
    },
    "promo_2": {
        "image": "https://i.imgur.com/8zQnF4T.jpeg",
        "caption": (
            "🎁 *VIP CASHBACK*\n\n"
            "✅ Weekly Cashback up to 15%\n"
            "✅ No Turnover\n\n"
            "🔥 VIP Exclusive Rewards"
        ),
        "buttons": [
            [InlineKeyboardButton("🚀 Join VIP", url="https://yourwebsite.com")],
            [InlineKeyboardButton("💬 Claim", url="https://t.me/your_support")]
        ]
    },
    "promo_3": {
        "image": "https://i.imgur.com/2gRkPjH.jpeg",
        "caption": (
            "💎 *DAILY RELOAD BONUS*\n\n"
            "✅ Daily bonus up to RM88\n"
            "✅ Unlimited claim\n\n"
            "⚡ Deposit & earn daily"
        ),
        "buttons": [
            [InlineKeyboardButton("🚀 Deposit", url="https://yourwebsite.com")],
            [InlineKeyboardButton("💬 Support", url="https://t.me/your_support")]
        ]
    }
}


# =========================
# 主菜单（收起状态）
# =========================
def base_keyboard():
    return ReplyKeyboardMarkup(
        [
            ["📋 MENU", "📌 About"],
            ["📞 Contact", "🚀 Register"]
        ],
        resize_keyboard=True
    )


# =========================
# 展开菜单（专业布局）
# =========================
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
# /start
# =========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "👋 Welcome!\n\n"
        "点击 MENU 打开 Promotion 系统 🔥"
    )

    await update.message.reply_photo(
        photo=MAIN_BANNER,
        caption=text,
        reply_markup=base_keyboard()
    )


# =========================
# Promotion 发送
# =========================
async def send_promo(update: Update, key: str):
    promo = PROMOTIONS.get(key)
    if not promo:
        await update.message.reply_text("❌ Promo not found.")
        return

    keyboard = promo["buttons"] + [
        [InlineKeyboardButton("⬅️ Back Menu", callback_data="back_menu")]
    ]

    await update.message.reply_photo(
        photo=promo["image"],
        caption=promo["caption"],
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# =========================
# About / Contact / Register
# =========================
async def send_about(update: Update):
    await update.message.reply_text(
        "📌 *About Us*\n\n"
        "✅ Fast Withdraw\n"
        "✅ 24/7 Support\n"
        "✅ Trusted Platform",
        parse_mode="Markdown"
    )


async def send_contact(update: Update):
    keyboard = [
        [InlineKeyboardButton("💬 Telegram", url="https://t.me/your_support")],
        [InlineKeyboardButton("💬 WhatsApp", url="https://wa.me/60139661818")]
    ]

    await update.message.reply_text(
        "📞 *Contact Us*",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def send_register(update: Update):
    keyboard = [
        [InlineKeyboardButton("🌍 Register Now", url="https://yourwebsite.com")]
    ]

    await update.message.reply_text(
        "🚀 *Register Now*",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# =========================
# 文本处理（Reply Keyboard）
# =========================
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message.text.strip()

    # MENU
    if msg == "📋 MENU":
        await update.message.reply_text(
            "🔥 Promotion Menu Opened",
            reply_markup=expanded_keyboard()
        )

    # CLOSE
    elif msg == "❌ Close":
        await update.message.reply_text(
            "Menu Closed",
            reply_markup=base_keyboard()
        )

    # BACK
    elif msg == "⬅️ Back":
        await update.message.reply_text(
            "Back to Menu",
            reply_markup=expanded_keyboard()
        )

    # PROMO
    elif msg == "🔥 Promo 1":
        await send_promo(update, "promo_1")

    elif msg == "🎁 Promo 2":
        await send_promo(update, "promo_2")

    elif msg == "💎 Promo 3":
        await send_promo(update, "promo_3")

    # ABOUT
    elif msg == "📌 About":
        await send_about(update)

    # CONTACT
    elif msg == "📞 Contact":
        await send_contact(update)

    # REGISTER
    elif msg == "🚀 Register":
        await send_register(update)

    else:
        await update.message.reply_text(
            "请点击 MENU 使用系统",
            reply_markup=base_keyboard()
        )


# =========================
# Inline button handler
# =========================
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "back_menu":
        await query.message.reply_text(
            "Back to Menu",
            reply_markup=expanded_keyboard()
        )


# =========================
# MAIN
# =========================
def main():
    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN not set")

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.add_handler(CallbackQueryHandler(button_handler))

    print("Bot running...")
    app.run_polling()


if __name__ == "__main__":
    main()
