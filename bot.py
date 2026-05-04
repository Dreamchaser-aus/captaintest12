import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")

# =========================
# 主菜单 Banner 图
# =========================
MAIN_BANNER = "https://i.imgur.com/4M7IWwP.jpeg"

# =========================
# Promotion 配置中心
# 以后你只需要改这里即可
# =========================
PROMOTIONS = {
    "promo_1": {
        "title": "🔥 Promo 1 - Welcome Bonus",
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
            [InlineKeyboardButton("💬 Contact Support", url="https://t.me/your_support")],
        ]
    },
    "promo_2": {
        "title": "🎁 Promo 2 - VIP Cashback",
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
            [InlineKeyboardButton("💬 Claim Cashback", url="https://t.me/your_support")],
        ]
    },
    "promo_3": {
        "title": "💎 Promo 3 - Daily Reload",
        "image": "https://i.imgur.com/2gRkPjH.jpeg",
        "caption": (
            "💎 *DAILY RELOAD BONUS*\n\n"
            "✅ Daily Reload up to RM88\n"
            "✅ Unlimited Claim\n"
            "✅ Suitable for all members\n\n"
            "⚡ Deposit & get extra bonus everyday!"
        ),
        "buttons": [
            [InlineKeyboardButton("🚀 Deposit Now", url="https://yourwebsite.com")],
            [InlineKeyboardButton("💬 Contact Admin", url="https://t.me/your_support")],
        ]
    }
}


# =========================
# 主菜单键盘（支持分页扩展）
# =========================
def main_menu_keyboard():
    keyboard = [
        [
            InlineKeyboardButton("🔥 Promo 1", callback_data="promo_1"),
            InlineKeyboardButton("🎁 Promo 2", callback_data="promo_2")
        ],
        [
            InlineKeyboardButton("💎 Promo 3", callback_data="promo_3"),
            InlineKeyboardButton("📌 About Us", callback_data="about_us")
        ],
        [
            InlineKeyboardButton("📞 Contact", callback_data="contact"),
            InlineKeyboardButton("🚀 Register", callback_data="register")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


# =========================
# /start
# =========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    caption_text = (
        "👋 *Welcome to our Official Promotion Center!*\n\n"
        "请选择你要查看的 Promotion 👇\n"
        "Click menu below to explore bonus & rewards 🔥"
    )

    await update.message.reply_photo(
        photo=MAIN_BANNER,
        caption=caption_text,
        parse_mode="Markdown",
        reply_markup=main_menu_keyboard()
    )


# =========================
# 显示 Promotion 详情（独立图片+文案）
# =========================
async def show_promotion(query, promo_key: str):
    promo = PROMOTIONS.get(promo_key)

    if not promo:
        await query.message.reply_text("❌ Promotion not found.")
        return

    keyboard = promo["buttons"] + [[InlineKeyboardButton("⬅️ Back to Menu", callback_data="back_home")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # 直接发送新图片广告（更像真实营销bot）
    await query.message.reply_photo(
        photo=promo["image"],
        caption=promo["caption"],
        parse_mode="Markdown",
        reply_markup=reply_markup
    )


# =========================
# 按钮回调处理
# =========================
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    # Promotion
    if data in PROMOTIONS:
        await show_promotion(query, data)

    # About Us
    elif data == "about_us":
        text = (
            "📌 *About Us*\n\n"
            "我们提供最稳定的游戏体验与最快的提款服务。\n\n"
            "✅ Fast Withdraw\n"
            "✅ 24/7 Support\n"
            "✅ Trusted Platform\n\n"
            "🔥 Join us and win everyday!"
        )

        keyboard = [
            [InlineKeyboardButton("🚀 Register Now", url="https://yourwebsite.com")],
            [InlineKeyboardButton("💬 Contact Support", url="https://t.me/your_support")],
            [InlineKeyboardButton("⬅️ Back to Menu", callback_data="back_home")]
        ]

        await query.message.reply_photo(
            photo="https://i.imgur.com/4M7IWwP.jpeg",
            caption=text,
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    # Contact
    elif data == "contact":
        text = (
            "📞 *Contact Us*\n\n"
            "💬 Telegram Support: @your_support\n"
            "📲 WhatsApp: +60 13-966 1818\n\n"
            "点击下面按钮即可直接联系 👇"
        )

        keyboard = [
            [InlineKeyboardButton("💬 Telegram Support", url="https://t.me/your_support")],
            [InlineKeyboardButton("💬 WhatsApp", url="https://wa.me/60139661818")],
            [InlineKeyboardButton("⬅️ Back to Menu", callback_data="back_home")]
        ]

        await query.message.reply_text(
            text=text,
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    # Register
    elif data == "register":
        text = (
            "🚀 *Register Now*\n\n"
            "点击下方链接注册账号：\n\n"
            "🌍 https://yourwebsite.com\n\n"
            "注册后联系管理员领取奖励 🎁"
        )

        keyboard = [
            [InlineKeyboardButton("🌍 Register Link", url="https://yourwebsite.com")],
            [InlineKeyboardButton("💬 Contact Support", url="https://t.me/your_support")],
            [InlineKeyboardButton("⬅️ Back to Menu", callback_data="back_home")]
        ]

        await query.message.reply_text(
            text=text,
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    # Back Home
    elif data == "back_home":
        caption_text = (
            "👋 *Promotion Menu*\n\n"
            "请选择你要查看的 Promotion 👇\n"
            "Click menu below to explore bonus & rewards 🔥"
        )

        await query.message.reply_photo(
            photo=MAIN_BANNER,
            caption=caption_text,
            parse_mode="Markdown",
            reply_markup=main_menu_keyboard()
        )


# =========================
# main
# =========================
def main():
    if not BOT_TOKEN:
        raise ValueError("❌ BOT_TOKEN not found. Please set BOT_TOKEN in Railway variables.")

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))

    print("✅ Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()
