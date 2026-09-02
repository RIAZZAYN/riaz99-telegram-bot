import os
import threading
from flask import Flask
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, LinkPreviewOptions
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters

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
UPI_ID = "8876178391@paytm"  # Tumhara UPI ID

def get_main_menu_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🟢 🛒 Buy Now (Products & Panels)", callback_data="buy_now", style="success")],
        [InlineKeyboardButton("📜 Deposit + Key History", callback_data="history")],
        [InlineKeyboardButton("🟢 💳 Add Balance (₹)", callback_data="add_balance", style="success"), InlineKeyboardButton("❓ How To Use", callback_data="how_to_use")],
        [InlineKeyboardButton("🔴 💬 Support (Admin)", callback_data="support", style="danger")]
    ])

async def main_menu(update, context):
    context.user_data['waiting_for_custom_amount'] = False
    text = (
        f'<a href="{BANNER_URL}">&#8203;</a>'
        "<b>👑 RIAZ 99 STORE 👑</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "<blockquote expandable>\n"
        "├ 🛒 <b>Buy Now :</b> Click below to see all products & panels (Bala Mods, etc.)\n"
        "├ 💳 <b>Add Balance :</b> Select or enter custom deposit amount\n"
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

async def add_balance_callback(update, context):
    context.user_data['waiting_for_custom_amount'] = False
    query = update.callback_query
    await query.answer()

    amount_keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("💵 ₹50", callback_data="amt_50"), InlineKeyboardButton("💵 ₹100", callback_data="amt_100")],
        [InlineKeyboardButton("💵 ₹200", callback_data="amt_200"), InlineKeyboardButton("💵 ₹500", callback_data="amt_500")],
        [InlineKeyboardButton("💵 ₹1000", callback_data="amt_1000"), InlineKeyboardButton("✏️ Custom Amount", callback_data="amt_custom")],
        [InlineKeyboardButton("🔴 ⬅️ Back to Main Menu", callback_data="main_menu", style="danger")]
    ])

    text = (
        "<b>💳 ADD BALANCE - SELECT AMOUNT</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "Choose a quick preset or tap <b>Custom Amount</b> to enter any value (e.g. ₹1, ₹10, ₹250):"
    )
    await query.edit_message_text(text, parse_mode="HTML", reply_markup=amount_keyboard)

async def custom_amount_prompt(update, context):
    query = update.callback_query
    await query.answer()
    
    # State set kar rahe hain ki ab user message bheje toh wo amount mana jaye
    context.user_data['waiting_for_custom_amount'] = True

    cancel_keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔴 ⬅️ Back to Main Menu", callback_data="main_menu", style="danger")]
    ])

    text = (
        "<b>✏️ ENTER CUSTOM AMOUNT</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "Niche chat box me jitna amount deposit karna hai wo number likhkar bhejo:\n\n"
        "<i>Example: <code>1</code>, <code>10</code>, <code>150</code>, <code>2500</code></i>"
    )
    await query.edit_message_text(text, parse_mode="HTML", reply_markup=cancel_keyboard)

async def handle_custom_amount_text(update, context):
    # Agar bot user se amount text ki umeed kar raha hai
    if context.user_data.get('waiting_for_custom_amount'):
        user_input = update.message.text.strip()
        
        if user_input.isdigit() and int(user_input) > 0:
            amount = user_input
            context.user_data['waiting_for_custom_amount'] = False
            
            qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=300x300&data=upi://pay?pa={UPI_ID}%26pn=RIAZ99%26am={amount}%26cu=INR"

            pay_keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("✅ Send Screenshot to Admin", url="https://t.me/riaz_zayn")],
                [InlineKeyboardButton("🔴 ⬅️ Back to Main Menu", callback_data="main_menu", style="danger")]
            ])

            text = (
                f'<a href="{qr_url}">&#8203;</a>'
                f"<b>⚡ SCAN & PAY ₹{amount} ⚡</b>\n"
                "━━━━━━━━━━━━━━━━━━━━━━\n"
                f"<b>Amount:</b> <code>₹{amount}</code>\n"
                f"<b>UPI ID:</b> <code>{UPI_ID}</code>\n\n"
                "<b>Instructions:</b>\n"
                "1. Upar dikh rahe QR code ko scan karke payment karein.\n"
                "2. Payment hone ke baad <b>Screenshot + Transaction ID (UTR)</b> Admin ko bhejein.\n"
                "3. Admin aapka balance 2 minutes me update kar dega!"
            )
            preview_options = LinkPreviewOptions(is_disabled=False, url=qr_url, prefer_large_media=True)
            await update.message.reply_text(text, parse_mode="HTML", reply_markup=pay_keyboard, link_preview_options=preview_options)
        else:
            await update.message.reply_text("❌ Please send a valid number (e.g. 1, 50, 100). Try again!")

async def generate_qr_callback(update, context):
    query = update.callback_query
    await query.answer()

    amount = query.data.split("_")[1]
    qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=300x300&data=upi://pay?pa={UPI_ID}%26pn=RIAZ99%26am={amount}%26cu=INR"

    pay_keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Send Screenshot to Admin", url="https://t.me/riaz_zayn")],
        [InlineKeyboardButton("🔴 ⬅️ Back to Main Menu", callback_data="main_menu", style="danger")]
    ])

    text = (
        f'<a href="{qr_url}">&#8203;</a>'
        f"<b>⚡ SCAN & PAY ₹{amount} ⚡</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        f"<b>Amount:</b> <code>₹{amount}</code>\n"
        f"<b>UPI ID:</b> <code>{UPI_ID}</code>\n\n"
        "<b>Instructions:</b>\n"
        "1. Upar dikh rahe QR code ko scan karke payment karein.\n"
        "2. Payment hone ke baad <b>Screenshot + Transaction ID (UTR)</b> Admin ko bhejein.\n"
        "3. Admin aapka balance 2 minutes me update kar dega!"
    )
    preview_options = LinkPreviewOptions(is_disabled=False, url=qr_url, prefer_large_media=True)
    await query.edit_message_text(text, parse_mode="HTML", reply_markup=pay_keyboard, link_preview_options=preview_options)

async def buy_now_callback(update, context):
    query = update.callback_query
    await query.answer()

    buy_keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("💬 Contact Admin to Buy", url="https://t.me/riaz_zayn")],
        [InlineKeyboardButton("🔴 ⬅️ Back to Main Menu", callback_data="main_menu", style="danger")]
    ])

    text = (
        "<b>🛒 PRODUCTS & PANELS STORE</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "<i>Available items:</i>\n"
        "• Bala Mods Panel\n"
        "• Gaming Keys & Subscriptions\n\n"
        "<b>Contact Admin directly to purchase:</b>\n"
        "<b>Telegram:</b> @riaz_zayn\n"
        "<b>WhatsApp:</b> +91 88761 78391"
    )
    await query.edit_message_text(text, parse_mode="HTML", reply_markup=buy_keyboard)

async def how_to_use_callback(update, context):
    query = update.callback_query
    await query.answer()

    how_keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔴 ⬅️ Back to Main Menu", callback_data="main_menu", style="danger")]
    ])

    text = (
        "<b>❓ HOW TO USE THE BOT</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "1. Tap <b>Add Balance</b> and select or enter an amount to generate a QR code.\n"
        "2. Pay via UPI and send screenshot to Admin.\n"
        "3. Balance add hone ke baad <b>Buy Now</b> se keys/panels kharidein!"
    )
    await query.edit_message_text(text, parse_mode="HTML", reply_markup=how_keyboard)

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
        "<i>If you face any payment or key issues, contact us directly:</i>\n\n"
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

# --- Execution Entry Point ---
if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()

    TOKEN = os.environ.get("BOT_TOKEN")
    
    if not TOKEN:
        print("Error: BOT_TOKEN not found in environment variables!")
        exit(1)

    app_bot = ApplicationBuilder().token(TOKEN).build()

    # Handlers Registration
    app_bot.add_handler(CommandHandler("start", main_menu))
    app_bot.add_handler(CallbackQueryHandler(main_menu, pattern="^main_menu$"))
    app_bot.add_handler(CallbackQueryHandler(buy_now_callback, pattern="^buy_now$"))
    app_bot.add_handler(CallbackQueryHandler(how_to_use_callback, pattern="^how_to_use$"))
    app_bot.add_handler(CallbackQueryHandler(support_callback, pattern="^support$"))
    app_bot.add_handler(CallbackQueryHandler(history_callback, pattern="^history$"))
    app_bot.add_handler(CallbackQueryHandler(add_balance_callback, pattern="^add_balance$"))
    app_bot.add_handler(CallbackQueryHandler(custom_amount_prompt, pattern="^amt_custom$"))
    app_bot.add_handler(CallbackQueryHandler(generate_qr_callback, pattern="^amt_"))
    
    # Text input handler for custom amount
    app_bot.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_custom_amount_text))

    print("Bot is polling...")
    app_bot.run_polling()
