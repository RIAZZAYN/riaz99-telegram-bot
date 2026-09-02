import os
import threading
from flask import Flask
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, LinkPreviewOptions
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler

# --- Flask Web Server Setup (For Render Port Binding) ---
app = Flask(__name__)

@app.route('/')
def home():
    return "RIAZ 99 Bot is Live 24/7!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

# --- Telegram Bot Configurations ---
BANNER_URL = "https://files.catbox.moe/itqjoi.jpg"

def get_main_menu_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🟢 🛒 Buy Now (Products & Panels)", callback_data="buy_now", style="success")],
        [InlineKeyboardButton("📜 Deposit + Key History", callback_data="history")],
        [InlineKeyboardButton("🟢 💳 Add Balance (₹)", callback_data="add_balance", style="success"), InlineKeyboardButton("❓ How To Use", callback_data="how_to_use")],
        [InlineKeyboardButton("🔴 💬 Support (Admin)", callback_data="support", style="danger")]
    ])

async def main_menu(update, context):
    text = (
        f'<a href="{BANNER_URL}">&#8203;</a>'
        "<b>👑 RIAZ 99 STORE 👑</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "<blockquote expandable>\n"
        "├ 🛒 <b>Buy Now :</b> Click below to see all products & panels (Bala Mods, etc.)\n"
        "├ 💳 <b>Add Balance :</b> Input custom deposit amount & verify transaction\n"
        "├ 📜 <b>Deposit + Key History :</b> View all your past deposits & purchased keys\n"
        "├ ❓ <b>How To Use :</b> Watch step-by-step video guide\n"
        "└ 💬 <b>Support :</b> Contact via Telegram, Instagram & WhatsApp\n"
        "</blockquote>\n\n"
        "💰 <b>Your Balance:</b> <code>₹0.00</code> 💵\n\n"
        "👇 <b>Select an option from the menu below:</b>"
    )

    preview_options = LinkPreviewOptions(is_disabled=False, url=BANNER_URL, prefer_large_media=True)

    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(text, parse_mode="HTML", reply_markup=get_main_menu_keyboard(), link_preview_options=preview_options)
    else:
        await update.message.reply_text(text, parse_mode="HTML", reply_markup=get_main_menu_keyboard(), link_preview_options=preview_options)

async def support_callback(update, context):
    query = update.callback_query
    await query.answer()

    support_keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("✈️ Telegram Support", url="https://t.me/riaz_zayn")],
        [InlineKeyboardButton("📸 Instagram", url="https://www.instagram.com/riaz_zayn/"), InlineKeyboardButton("💬 WhatsApp", url="https://wa.me/918876178391")],
        [InlineKeyboardButton("🔴 ⬅️ Back to Main Menu", callback_data="main_menu", style="danger")]
    ])

    text = (
        "<b>📞 RIAZ 99 OFFICIAL SUPPORT</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "<i>If you face any payment or key issues, contact us directly through the links below:</i>\n\n"
        "<b>Telegram:</b> @riaz_zayn\n"
        "<b>WhatsApp:</b> +91 88761 78391"
    )
    await query.edit_message_text(text, parse_mode="HTML", reply_markup=support_keyboard)

async def history_callback(update, context):
    query = update.callback_query
    await query.answer()

    history_keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📥 Deposit History", callback_data="view_deposits"), InlineKeyboardButton("🔑 Key History", callback_data="view_keys")],
        [InlineKeyboardButton("🔴 ⬅️ Back to Main Menu", callback_data="main_menu", style="danger")]
    ])

    text = (
        "<b>📜 YOUR ACCOUNT HISTORY</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "<i>Select which history you want to check:</i>"
    )
    await query.edit_message_text(text, parse_mode="HTML", reply_markup=history_keyboard)

async def add_balance_callback(update, context):
    query = update.callback_query
    await query.answer()

    balance_keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("✈️ Contact via Telegram", url="https://t.me/riaz_zayn")],
        [InlineKeyboardButton("💬 Contact via WhatsApp", url="https://wa.me/918876178391")],
        [InlineKeyboardButton("🔴 ⬅️ Back to Main Menu", callback_data="main_menu", style="danger")]
    ])

    text = (
        "<b>💳 ADD BALANCE TO YOUR ACCOUNT</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "<i>Contact Admin to get payment details (UPI/QR Code) & verify your deposit:</i>\n\n"
        "<b>Telegram Admin:</b> @riaz_zayn\n"
        "<b>WhatsApp Admin:</b> +91 88761 78391\n\n"
        "<i>Send screenshot after completing payment!</i>"
    )
    await query.edit_message_text(text, parse_mode="HTML", reply_markup=balance_keyboard)

# --- Execution Entry Point ---
if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()

    TOKEN = os.environ.get("BOT_TOKEN")
    
    if not TOKEN:
        print("Error: BOT_TOKEN not found in environment variables!")
        exit(1)

    app_bot = ApplicationBuilder().token(TOKEN).build()

    app_bot.add_handler(CommandHandler("start", main_menu))
    app_bot.add_handler(CallbackQueryHandler(main_menu, pattern="^main_menu$"))
    app_bot.add_handler(CallbackQueryHandler(support_callback, pattern="^support$"))
    app_bot.add_handler(CallbackQueryHandler(history_callback, pattern="^history$"))
    app_bot.add_handler(CallbackQueryHandler(add_balance_callback, pattern="^add_balance$"))

    print("Bot is polling...")
    app_bot.run_polling()
