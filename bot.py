import os
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove
)
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters
)

BOT_TOKEN = os.getenv("BOT_TOKEN")

MAIN_BANNER = "https://i.imgur.com/4M7IWwP.jpeg"

PROMOTIONS = {
    "promo_1": {
        "name": "🔥 Promo 1",
        "image": "https://i.imgur.com/5qHnQ0R.jpeg",
        "caption": (
            "🔥 *WELCOME BONUS*\n\n"
            "✅ Deposit RM50 Free RM10\n"
            "✅ Instant Credit\n"
            "✅ Fast Withdraw\n\n"
            "📌 *Limited Offer Today Only!*"
        ),
        "buttons": [
            [InlineKeyboardButton("🚀 Register Now", url="https://yourwebsite.com")],
            [InlineKeyboardButton("💬 Contact Support", url="https://t.me/your_support")]
        ]
    },
    "promo_2": {
        "name": "🎁 Promo 2",
        "image": "https://i.imgur.com/8zQnF4T.jpeg",
        "caption": (
            "🎁 *VIP CASHBACK*\n\n"
            "✅ Weekly Cashback up to 15%\n"
            "✅ No Turnover Required\n"
            "✅ VIP Exclusive Reward\n\n"
            "🔥 *Join VIP now and earn more!*"
        ),
        "buttons": [
            [InlineKeyboardButton("🚀 Join VIP", url="https://yourwebsite.com")],
            [InlineKeyboardButton("💬 Claim Cashback", url="https://t.me/your_support")]
        ]
    },
    "promo_3": {
        "name": "💎 Promo 3",
        "image": "https://i.imgur.com/2gRkPjH.jpeg",
        "caption": (
            "💎 *DAILY RELOAD BONUS*\n\n"
            "✅ Daily Reload up to RM88\n"
            "✅ Unlimited Claim\n\n"
            "⚡ Deposit & get extra bonus everyday!"
        ),
        "buttons": [
            [InlineKeyboardButton("🚀 Deposit Now", url="https://yourwebsite.com")],
            [InlineKeyboardButton("💬 Contact Admin", url="https://t.me/your_support")]
        ]
    }
}

# =========================
# Reply Keyboard - 初始（只显示 MENU）
# =========================
def collapsed_menu():
    return ReplyKeyboardMarkup(
        [["📋 MENU"]],
        resize_keyboard=True,
        one_time_keyboard=False
    )

# =========================
# Reply Keyboard - 展开菜单
# =========================
def expanded_menu():
    keyboard = [
        ["🔥 Promo 1", "🎁 Promo 2"],
        ["💎 Promo 3", "📌 About Us"],
        ["📞 Contact", "🚀 Register"],
        ["❌ Close Menu"]
    ]
    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,
        one_time_keyboard=False
    )

# =========================
# 发送 Promotion 广告图 + 文案
# =========================
async def send_promo(update: Update, promo_key: str):
    promo = PROMOTIONS.get(promo_key)
    if not promo:
        await update.message.reply_text("❌ Promotion not found.")
        return

    inline_keyboard = promo["buttons"] + [
        [InlineKeyboardButton("⬅️ Back Menu", callback_data="back_menu")]
    ]

    await update.message.reply_photo(
        photo=promo["image"],
        caption=promo["caption"],
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(inline_keyboard)
    )

# =========================
# /start
# =========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "👋 Welcome!\n\n"
        "点击下方 📋 MENU 按钮打开活动菜单 🔥"
    )

    await update.message.reply_photo(
        photo=MAIN_BANNER,
        caption=text,
        reply_markup=collapsed_menu()
    )

# =========================
# 处理 Reply Keyboard 输入
# =========================
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message.text.strip()

    # 展开菜单
    if msg == "📋 MENU":
        await update.message.reply_text(
            "✅ Menu Opened. 请选择 Promotion 👇",
            reply_markup=expanded_menu()
        )

    # 关闭菜单
    elif msg == "❌ Close Menu":
        await update.message.reply_text(
            "✅ Menu Closed.",
            reply_markup=collapsed_menu()
        )

    # Promotions
    elif msg == "🔥 Promo 1":
        await send_promo(update, "promo_1")

    elif msg == "🎁 Promo 2":
        await send_promo(update, "promo_2")

    elif msg == "💎 Promo 3":
        await send_promo(update, "promo_3")

    # About Us
    elif msg == "📌 About Us":
        text = (
            "📌 *About Us*\n\n"
            "✅ Fast Withdraw\n"
            "✅ 24/7 Support\n"
            "✅ Trusted Platform\n\n"
            "🔥 Trusted by thousands of players!"
        )
        await update.message.reply_text(text, parse_mode="Markdown")

    # Contact
    elif msg == "📞 Contact":
        text = (
            "📞 *Contact Us*\n\n"
            "Telegram: @your_support\n"
            "WhatsApp: +60 13-966 1818"
        )
        keyboard = [
            [InlineKeyboardButton("💬 Telegram Support", url="https://t.me/your_support")],
            [InlineKeyboardButton("💬 WhatsApp", url="https://wa.me/60139661818")]
        ]
        await update.message.reply_text(
            text,
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    # Register
    elif msg == "🚀 Register":
        text = (
            "🚀 *Register Now*\n\n"
            "点击下面按钮注册："
        )
        keyboard = [
            [InlineKeyboardButton("🌍 Register Link", url="https://yourwebsite.com")],
            [InlineKeyboardButton("💬 Contact Support", url="https://t.me/your_support")]
        ]
        await update.message.reply_text(
            text,
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    else:
        await update.message.reply_text(
            "请点击 📋 MENU 打开菜单 👇",
            reply_markup=collapsed_menu()
        )

# =========================
# Inline 回调按钮处理
# =========================
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "back_menu":
        await query.message.reply_text(
            "✅ 返回菜单，请继续选择 👇",
            reply_markup=expanded_menu()
        )

# =========================
# main
# =========================
def main():
    if not BOT_TOKEN:
        raise ValueError("❌ BOT_TOKEN not found. Please set BOT_TOKEN in Railway variables.")

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.add_handler(CallbackQueryHandler(button_handler))

    print("✅ Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
