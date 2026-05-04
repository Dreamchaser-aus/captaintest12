import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")  # 从 Railway env 读取 token

WELCOME_IMAGE_URL = "https://i.imgur.com/4M7IWwP.jpeg"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("🔥 Promo 1", callback_data="promo_1"),
            InlineKeyboardButton("🎁 Promo 2", callback_data="promo_2")
        ],
        [
            InlineKeyboardButton("📌 About Us", callback_data="about_us"),
            InlineKeyboardButton("📞 Contact", callback_data="contact")
        ],
        [
            InlineKeyboardButton("🚀 Join Now", callback_data="join_now")
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    caption_text = (
        "👋 Welcome!\n\n"
        "请选择你要查看的内容：\n"
        "Click the buttons below 👇"
    )

    await update.message.reply_photo(
        photo=WELCOME_IMAGE_URL,
        caption=caption_text,
        reply_markup=reply_markup
    )


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "promo_1":
        text = (
            "🔥 Promo 1 活动内容\n\n"
            "✅ Deposit RM50 Free RM10\n"
            "✅ Valid Today Only\n\n"
            "📌 点击 Join Now 立刻参与"
        )
        keyboard = [
            [InlineKeyboardButton("🚀 Join Now", url="https://google.com")],
            [InlineKeyboardButton("⬅️ Back", callback_data="back_home")]
        ]
        await query.edit_message_caption(
            caption=text,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif data == "promo_2":
        text = (
            "🎁 Promo 2 活动内容\n\n"
            "✅ Deposit RM100 Free RM30\n"
            "✅ Unlimited Claim\n\n"
            "⚡ 速度来拿奖励"
        )
        keyboard = [
            [InlineKeyboardButton("🚀 Join Now", url="https://google.com")],
            [InlineKeyboardButton("⬅️ Back", callback_data="back_home")]
        ]
        await query.edit_message_caption(
            caption=text,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif data == "about_us":
        text = (
            "📌 About Us\n\n"
            "我们提供最稳定的服务与最快的出款。\n"
            "24小时在线客服。\n\n"
            "🔥 Trusted Platform | Fast Withdraw"
        )
        keyboard = [
            [InlineKeyboardButton("📞 Contact", callback_data="contact")],
            [InlineKeyboardButton("⬅️ Back", callback_data="back_home")]
        ]
        await query.edit_message_caption(
            caption=text,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif data == "contact":
        text = (
            "📞 Contact Us\n\n"
            "WhatsApp: +60 13-966 1818\n"
            "Telegram Support: @your_support\n\n"
            "点击下面按钮直接联系 👇"
        )
        keyboard = [
            [InlineKeyboardButton("💬 WhatsApp", url="https://wa.me/60139661818")],
            [InlineKeyboardButton("💬 Telegram Support", url="https://t.me/your_support")],
            [InlineKeyboardButton("⬅️ Back", callback_data="back_home")]
        ]
        await query.edit_message_caption(
            caption=text,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif data == "join_now":
        text = (
            "🚀 Join Now\n\n"
            "点击下方链接马上注册：\n\n"
            "👉 https://yourwebsite.com\n\n"
            "注册后联系管理员即可领取奖励 🎁"
        )
        keyboard = [
            [InlineKeyboardButton("🌍 Register Now", url="https://yourwebsite.com")],
            [InlineKeyboardButton("⬅️ Back", callback_data="back_home")]
        ]
        await query.edit_message_caption(
            caption=text,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif data == "back_home":
        keyboard = [
            [
                InlineKeyboardButton("🔥 Promo 1", callback_data="promo_1"),
                InlineKeyboardButton("🎁 Promo 2", callback_data="promo_2")
            ],
            [
                InlineKeyboardButton("📌 About Us", callback_data="about_us"),
                InlineKeyboardButton("📞 Contact", callback_data="contact")
            ],
            [
                InlineKeyboardButton("🚀 Join Now", callback_data="join_now")
            ]
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)

        caption_text = (
            "👋 Welcome Back!\n\n"
            "请选择你要查看的内容：\n"
            "Click the buttons below 👇"
        )

        await query.edit_message_caption(
            caption=caption_text,
            reply_markup=reply_markup
        )


def main():
    if not BOT_TOKEN:
        raise ValueError("❌ BOT_TOKEN not found. Please set BOT_TOKEN in Railway environment variables.")

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))

    print("✅ Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()
