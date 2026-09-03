import os
import threading
from flask import Flask
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters

# --- Flask Web Server Setup (for UptimeRobot) ---
app = Flask(__name__)

@app.route('/')
def home():
    return "RIAZ 99 Bot is Live 24/7!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

# --- Telegram Bot Configurations ---
BANNER_URL = "https://files.catbox.moe/itqjoi.jpg"
UPI_ID = "riaz99@slc"
# Naya Clean Google Pay QR Image URL
QR_IMAGE_URL = "https://files.catbox.moe/vzcxdz.jpeg"

def get_main_menu_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🟢 🛒 Buy Now (Products & Panels)", callback_data="buy_now")],
        [InlineKeyboardButton("📜 Deposit + Key History", callback_data="history")],
        [InlineKeyboardButton("🟢 💳 Add Balance (₹)", callback_data="add_balance"), InlineKeyboardButton("❓ How To Use", callback_data="how_to_use")],
        [InlineKeyboardButton("🔴 💬 Support (Admin)", callback_data="support")]
    ])

async def main_menu(update, context):
    context.user_data['custom_amount_str'] = ""
    context.user_data['in_keypad_mode'] = False

    text = (
        "<b>👑 RIAZ 99 STORE 👑</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "<blockquote expandable>\n"
        "├ 🛒 <b>Buy Now :</b> Click below to see all products & panels\n"
        "├ 💳 <b>Add Balance :</b> Select amount or use custom keypad\n"
        "├ 📜 <b>Deposit + Key History :</b> View all your past deposits & purchased keys\n"
        "├ ❓ <b>How To Use :</b> Watch step-by-step video guide\n"
        "└ 💬 <b>Support :</b> Contact via Telegram, Instagram & WhatsApp\n"
        "</blockquote>\n\n"
        "💰 <b>Your Balance:</b> <code>₹0.00</code> 💵\n\n"
        "👇 <b>Select an option from the menu below:</b>"
    )

    if update.callback_query:
        query = update.callback_query
        await query.answer()
        try:
            await query.message.edit_media(
                media=InputMediaPhoto(media=BANNER_URL, caption=text, parse_mode="HTML"),
                reply_markup=get_main_menu_keyboard()
            )
        except Exception:
            await query.edit_message_text(text, parse_mode="HTML", reply_markup=get_main_menu_keyboard())
    else:
        await update.message.reply_photo(photo=BANNER_URL, caption=text, parse_mode="HTML", reply_markup=get_main_menu_keyboard())

# --- ADD BALANCE MENU ---
async def add_balance_callback(update, context):
    context.user_data['custom_amount_str'] = ""
    context.user_data['in_keypad_mode'] = False
    query = update.callback_query
    await query.answer()

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("💵 ₹50", callback_data="amt_50"), InlineKeyboardButton("💵 ₹100", callback_data="amt_100")],
        [InlineKeyboardButton("💵 ₹200", callback_data="amt_200"), InlineKeyboardButton("💵 ₹500", callback_data="amt_500")],
        [InlineKeyboardButton("💵 ₹1000", callback_data="amt_1000"), InlineKeyboardButton("⌨️ TYPE CUSTOM AMOUNT", callback_data="keypad_open")],
        [InlineKeyboardButton("🔴 ⬅️ Back to Main Menu", callback_data="main_menu")]
    ])

    text = (
        "<b>💳 ADD BALANCE - SELECT AMOUNT</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "Choose a quick preset amount or tap <b>⌨️ TYPE CUSTOM AMOUNT</b> to open keypad:"
    )
    
    try:
        await query.message.edit_media(
            media=InputMediaPhoto(media=BANNER_URL, caption=text, parse_mode="HTML"),
            reply_markup=keyboard
        )
    except Exception:
        await query.edit_message_text(text, parse_mode="HTML", reply_markup=keyboard)

# --- KEYPAD LOGIC ---
def build_keypad_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("1", callback_data="kp_1"), InlineKeyboardButton("2", callback_data="kp_2"), InlineKeyboardButton("3", callback_data="kp_3")],
        [InlineKeyboardButton("4", callback_data="kp_4"), InlineKeyboardButton("5", callback_data="kp_5"), InlineKeyboardButton("6", callback_data="kp_6")],
        [InlineKeyboardButton("7", callback_data="kp_7"), InlineKeyboardButton("8", callback_data="kp_8"), InlineKeyboardButton("9", callback_data="kp_9")],
        [InlineKeyboardButton("❌ CLEAR", callback_data="kp_clear"), InlineKeyboardButton("0", callback_data="kp_0"), InlineKeyboardButton("➡️ BACK", callback_data="kp_back")],
        [InlineKeyboardButton("🟢 ✅ CONFIRM AMOUNT", callback_data="kp_confirm")],
        [InlineKeyboardButton("🔴 ⬅️ Return to Quick Amounts", callback_data="add_balance")]
    ])

async def keypad_open_callback(update, context):
    query = update.callback_query
    await query.answer()

    context.user_data['custom_amount_str'] = ""
    context.user_data['in_keypad_mode'] = True

    text = (
        "<b>✏️ ENTER CUSTOM AMOUNT</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "<b>Amount: ₹0</b>\n\n"
        "Use the keypad below or type amount directly in chat.\n\n"
        "<i>Min: ₹1.00 | Max: ₹50,000.00</i>"
    )
    try:
        await query.message.edit_media(
            media=InputMediaPhoto(media=BANNER_URL, caption=text, parse_mode="HTML"),
            reply_markup=build_keypad_keyboard()
        )
    except Exception:
        await query.edit_message_text(text, parse_mode="HTML", reply_markup=build_keypad_keyboard())

async def keypad_press_callback(update, context):
    query = update.callback_query
    action = query.data.replace("kp_", "")
    
    if action == "confirm":
        await keypad_confirm_action(query, context)
        return

    await query.answer()
    amt_str = context.user_data.get('custom_amount_str', "")

    if action.isdigit():
        if len(amt_str) < 6:
            amt_str += action
    elif action == "clear":
        amt_str = ""
    elif action == "back":
        amt_str = amt_str[:-1]

    context.user_data['custom_amount_str'] = amt_str
    display_val = amt_str if amt_str != "" else "0"

    text = (
        "<b>✏️ ENTER CUSTOM AMOUNT</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        f"<b>Amount: ₹{display_val}</b>\n\n"
        "Use the keypad below or type amount directly in chat.\n\n"
        "<i>Min: ₹1.00 | Max: ₹50,000.00</i>"
    )
    try:
        await query.message.edit_media(
            media=InputMediaPhoto(media=BANNER_URL, caption=text, parse_mode="HTML"),
            reply_markup=build_keypad_keyboard()
        )
    except Exception:
        await query.edit_message_text(text, parse_mode="HTML", reply_markup=build_keypad_keyboard())

async def keypad_confirm_action(query, context):
    amt_str = context.user_data.get('custom_amount_str', "0")
    if not amt_str or amt_str == "" or int(amt_str) <= 0:
        await query.answer("❌ Please enter a valid amount greater than ₹0!", show_alert=True)
        return

    await query.answer()
    context.user_data['in_keypad_mode'] = False
    amount = int(amt_str)
    await show_qr_screen_direct(query, amount)

async def handle_text_input(update, context):
    if context.user_data.get('in_keypad_mode'):
        text_input = update.message.text.strip()
        if text_input.isdigit() and int(text_input) > 0:
            context.user_data['custom_amount_str'] = text_input
            context.user_data['in_keypad_mode'] = False
            amount = int(text_input)

            pay_keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("🟢 ✅ VERIFY PAYMENT", url="https://t.me/riaz_zayn")],
                [InlineKeyboardButton("🔴 ⬅️ Back to Main Menu", callback_data="main_menu")]
            ])
            text = (
                "<b>⚡ RIAZ 99 STORE — UPI QR ACTIVE ⚡</b>\n"
                "━━━━━━━━━━━━━━━━━━━━━━\n"
                "<b>Merchant Name:</b> RIAZ 99 STORE\n\n"
                f"Scan & pay exactly <code>₹{amount}.00</code>\n\n"
                f"<b>UPI ID:</b> <code>{UPI_ID}</code>\n\n"
                "Tap <b>VERIFY PAYMENT</b> below after completing payment.\n\n"
                "<i>⏳ Session expires in 5 minutes.</i>"
            )
            await update.message.reply_photo(photo=QR_IMAGE_URL, caption=text, parse_mode="HTML", reply_markup=pay_keyboard)

# --- QR CODE GENERATOR SCREEN ---
async def preset_amount_callback(update, context):
    query = update.callback_query
    await query.answer()
    amount = query.data.split("_")[1]
    await show_qr_screen_direct(query, amount)

async def show_qr_screen_direct(query, amount):
    pay_keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🟢 ✅ VERIFY PAYMENT", url="https://t.me/riaz_zayn")],
        [InlineKeyboardButton("🔴 ⬅️ Back to Main Menu", callback_data="main_menu")]
    ])

    text = (
        "<b>⚡ RIAZ 99 STORE — UPI QR ACTIVE ⚡</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "<b>Merchant Name:</b> RIAZ 99 STORE\n\n"
        f"Scan & pay exactly <code>₹{amount}.00</code>\n\n"
        f"<b>UPI ID:</b> <code>{UPI_ID}</code>\n\n"
        "Tap <b>VERIFY PAYMENT</b> below after completing payment.\n\n"
        "<i>⏳ Session expires in 5 minutes.</i>"
    )

    try:
        await query.message.edit_media(
            media=InputMediaPhoto(media=QR_IMAGE_URL, caption=text, parse_mode="HTML"),
            reply_markup=pay_keyboard
        )
    except Exception:
        await query.message.reply_photo(photo=QR_IMAGE_URL, caption=text, parse_mode="HTML", reply_markup=pay_keyboard)

# --- OTHER SECTIONS ---
async def buy_now_callback(update, context):
    query = update.callback_query
    await query.answer()
    buy_keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("💬 Contact Admin to Buy", url="https://t.me/riaz_zayn")],
        [InlineKeyboardButton("🔴 ⬅️ Back to Main Menu", callback_data="main_menu")]
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
    try:
        await query.message.edit_media(
            media=InputMediaPhoto(media=BANNER_URL, caption=text, parse_mode="HTML"),
            reply_markup=buy_keyboard
        )
    except Exception:
        await query.edit_message_text(text, parse_mode="HTML", reply_markup=buy_keyboard)

async def history_callback(update, context):
    query = update.callback_query
    await query.answer()
    history_keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔴 ⬅️ Back to Main Menu", callback_data="main_menu")]
    ])
    text = (
        "<b>📜 DEPOSIT & KEY HISTORY</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "<i>Your past transactions and purchased keys will appear here.</i>\n\n"
        "No recent records found."
    )
    try:
        await query.message.edit_media(
            media=InputMediaPhoto(media=BANNER_URL, caption=text, parse_mode="HTML"),
            reply_markup=history_keyboard
        )
    except Exception:
        await query.edit_message_text(text, parse_mode="HTML", reply_markup=history_keyboard)

async def how_to_use_callback(update, context):
    query = update.callback_query
    await query.answer()
    how_keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔴 ⬅️ Back to Main Menu", callback_data="main_menu")]
    ])
    text = (
        "<b>❓ HOW TO USE THE BOT</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "1. Tap <b>Add Balance</b> and select an amount or use keypad to generate QR code.\n"
        "2. Pay via UPI and send screenshot to Admin.\n"
        "3. Balance add hone ke baad <b>Buy Now</b> se keys/panels kharidein!"
    )
    try:
        await query.message.edit_media(
            media=InputMediaPhoto(media=BANNER_URL, caption=text, parse_mode="HTML"),
            reply_markup=how_keyboard
        )
    except Exception:
        await query.edit_message_text(text, parse_mode="HTML", reply_markup=how_keyboard)

async def support_callback(update, context):
    query = update.callback_query
    await query.answer()
    support_keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("✈️ Telegram Support", url="https://t.me/riaz_zayn")],
        [InlineKeyboardButton("📸 Instagram", url="https://www.instagram.com/riaz_zayn/"), InlineKeyboardButton("💬 WhatsApp", url="https://wa.me/918876178391")],
        [InlineKeyboardButton("🔴 ⬅️ Back to Main Menu", callback_data="main_menu")]
    ])
    text = (
        "<b>📞 RIAZ 99 OFFICIAL SUPPORT</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "<i>If you face any payment or key issues, contact us directly:</i>\n\n"
        "<b>Telegram:</b> @riaz_zayn\n"
        "<b>WhatsApp:</b> +91 88761 78391"
    )
    try:
        await query.message.edit_media(
            media=InputMediaPhoto(media=BANNER_URL, caption=text, parse_mode="HTML"),
            reply_markup=support_keyboard
        )
    except Exception:
        await query.edit_message_text(text, parse_mode="HTML", reply_markup=support_keyboard)

def main():
    # Start Flask server thread for UptimeRobot
    t = threading.Thread(target=run_flask)
    t.daemon = True
    t.start()

    # Get Token from environment variables
    TOKEN = os.environ.get("BOT_TOKEN")
    if not TOKEN:
        print("❌ ERROR: BOT_TOKEN environment variable not found!")
        return

    application = ApplicationBuilder().token(TOKEN).build()

    # Handlers
    application.add_handler(CommandHandler("start", main_menu))
    application.add_handler(CallbackQueryHandler(main_menu, pattern="^main_menu$"))
    application.add_handler(CallbackQueryHandler(buy_now_callback, pattern="^buy_now$"))
    application.add_handler(CallbackQueryHandler(history_callback, pattern="^history$"))
    application.add_handler(CallbackQueryHandler(add_balance_callback, pattern="^add_balance$"))
    application.add_handler(CallbackQueryHandler(how_to_use_callback, pattern="^how_to_use$"))
    application.add_handler(CallbackQueryHandler(support_callback, pattern="^support$"))
    
    # Preset & Keypad Handlers
    application.add_handler(CallbackQueryHandler(preset_amount_callback, pattern="^amt_"))
    application.add_handler(CallbackQueryHandler(keypad_open_callback, pattern="^keypad_open$"))
    application.add_handler(CallbackQueryHandler(keypad_press_callback, pattern="^kp_"))
    
    # Text input handler for custom amount typing
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_input))

    print("🚀 RIAZ 99 Bot is starting...")
    application.run_polling()

if __name__ == "__main__":
    main()
