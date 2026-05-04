import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

TOKEN = os.getenv("BOT_TOKEN")


# ========= START =========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        ["📋 Menu", "ℹ️ About"]
    ]

    await update.message.reply_text(
        "欢迎使用 Bot 👋",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )


# ========= TEXT MENU =========
async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "📋 Menu":
        keyboard = [
            [InlineKeyboardButton("🔘 功能1", callback_data="func1")],
            [InlineKeyboardButton("🔘 功能2", callback_data="func2")],
            [InlineKeyboardButton("⬅️ 返回", callback_data="back")]
        ]

        await update.message.reply_text(
            "📋 主菜单：",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif text == "ℹ️ About":
        await update.message.reply_text("这是一个 Telegram Bot 🤖")


# ========= CALLBACK BUTTONS =========
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data

    if data == "func1":
        await query.edit_message_text("你点击了 功能1")

    elif data == "func2":
        await query.edit_message_text("你点击了 功能2")

    elif data == "back":
        keyboard = [
            [InlineKeyboardButton("📋 Menu", callback_data="menu")],
            [InlineKeyboardButton("ℹ️ About", callback_data="about")]
        ]
        await query.edit_message_text(
            "返回首页 👇",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif data == "menu":
        keyboard = [
            [InlineKeyboardButton("🔘 功能1", callback_data="func1")],
            [InlineKeyboardButton("🔘 功能2", callback_data="func2")]
        ]
        await query.edit_message_text(
            "📋 主菜单：",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif data == "about":
        await query.edit_message_text("这是一个 Telegram Bot 🤖")


# ========= MAIN =========
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))
    app.add_handler(CallbackQueryHandler(button_handler))

    print("Bot running...")
    app.run_polling()


if __name__ == "__main__":
    main()
