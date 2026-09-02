import os
import threading
from flask import Flask
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, LinkPreviewOptions
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters

# --- Flask Web Server Setup ---
app = Flask(__name__)

@app.route('/')
def home():
    return "RIAZ 99 Bot is Live 24/7!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

# --- Telegram Bot Configurations ---
BANNER_URL = "https://files.catbox.moe/itqjoi.jpg"
UPI_ID = "8876178391@paytm"

def get_main_menu_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🛒 Buy Now", callback_data="buy_now", style="danger")],
        [InlineKeyboardButton("🟢 Check Update", callback_data="check_update"), InlineKeyboardButton("💸 Add Balance", callback_data="add_balance")],
        [InlineKeyboardButton("👑 My Profile + All History", callback_data="history")],
        [InlineKeyboardButton("🔗 Refer And Earn", callback_data="refer"), InlineKeyboardButton("❓ How To Use Bot", callback_data="how_to_use")],
        [InlineKeyboardButton("✈️ Support", callback_data="support"), InlineKeyboardButton("🎁 Daily Gift", callback_data="daily_gift")]
    ])

async def main_menu(update, context):
    context.user_data['custom_amount_str'] = ""
    context.user_data['in_keypad_mode'] = False

    text = (
        f'<a href="{BANNER_URL}">&#8203;</a>'
        "<b>💖 RIAZ 99 STORE 💖</b>\n\n"
        "├ 🛒 <b>Buy Now :</b> All Key Purchase & Instant Delivery\n"
        "├ 🟢 <b>Check Update :</b> Check Setup Video And Update Apk\n"
        "├ 💸 <b>Add Balance :</b> Deposit Balance & Secure Auto-Add Payment System\n"
        "├ 👑 <b>My Profile + All History :</b> Check Your Account Information + All History\n"
        "├ 🔗 <b>Refer And Earn :</b> Share Refer Link & Earn Money\n"
        "├ ❓ <b>How To Use Bot :</b> View Tutorial And Work This Bot\n"
        "├ ✈️ <b>Support :</b> Bot Problem Fixed For Support Admin\n"
        "└ 🎁 <b>Daily Gift :</b> Free Spin and win random balance daily.\n\n"
        "<b>💸 Your Balance:</b> <code>₹0.00</code>\n\n"
        "👇 <b>Select an option from the menu below:</b>"
    )

    preview_options = LinkPreviewOptions(is_disabled=False, url=BANNER_URL, prefer_large_media=True)

    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(text, parse_mode="HTML", reply_markup=get_main_menu_keyboard(), link_preview_options=preview_options)
    else:
        await update.message.reply_text(text, parse_mode="HTML", reply_markup=get_main_menu_keyboard(), link_preview_options=preview_options)

# --- 1. ADD BALANCE MENU ---
async def add_balance_callback(update, context):
    context.user_data['custom_amount_str'] = ""
    context.user_data['in_keypad_mode'] = False
    query = update.callback_query
    await query.answer()

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("💸 ₹100", callback_data="amt_100"), InlineKeyboardButton("💸 ₹200", callback_data="amt_200")],
        [InlineKeyboardButton("💸 ₹500", callback_data="amt_500"), InlineKeyboardButton("💸 ₹1000", callback_data="amt_1000")],
        [InlineKeyboardButton("⌨️ TYPE CUSTOM AMOUNT", callback_data="keypad_open")],
        [InlineKeyboardButton("➡️ Back to Menu", callback_data="main_menu")]
    ])

    text = (
        "<b>➕ ADD FUNDS TO WALLET 💥</b>\n\n"
        "Choose a quick amount to add or type/use a custom one below.\n\n"
        "<i>💸 Predefined amounts are faster to process! 💥</i>"
    )
    await query.edit_message_text(text, parse_mode="HTML", reply_markup=keyboard)

# --- 2. KEYPAD UI ---
def build_keypad_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("1", callback_data="kp_1"), InlineKeyboardButton("2", callback_data="kp_2"), InlineKeyboardButton("3", callback_data="kp_3")],
        [InlineKeyboardButton("4", callback_data="kp_4"), InlineKeyboardButton("5", callback_data="kp_5"), InlineKeyboardButton("6", callback_data="kp_6")],
        [InlineKeyboardButton("7", callback_data="kp_7"), InlineKeyboardButton("8", callback_data="kp_8"), InlineKeyboardButton("9", callback_data="kp_9")],
        [InlineKeyboardButton("❌ CLEAR", callback_data="kp_clear"), InlineKeyboardButton("0", callback_data="kp_0"), InlineKeyboardButton("➡️ BACK", callback_data="kp_back")],
        [InlineKeyboardButton("✅ CONFIRM AMOUNT", callback_data="kp_confirm")],
        [InlineKeyboardButton("➡️ Return to Quick Amounts", callback_data="add_balance")]
    ])

async def keypad_open_callback(update, context):
    query = update.callback_query
    await query.answer()

    context.user_data['custom_amount_str'] = ""
    context.user_data['in_keypad_mode'] = True

    text = (
        "<b>📝 ENTER CUSTOM AMOUNT 💥</b>\n\n"
        "Amount: ₹0\n\n"
        "Use the keypad below to enter amount or type directly in chat.\n\n"
        "Min: 💸 ₹1.00 | Max: 💸 ₹50,000.00"
    )
    await query.edit_message_text(text, parse_mode="HTML", reply_markup=build_keypad_keyboard())

async def keypad_press_callback(update, context):
    query = update.callback_query
    await query.answer()

    action = query.data.replace("kp_", "")
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
        "<b>📝 ENTER CUSTOM AMOUNT 💥</b>\n\n"
        f"Amount: ₹{display_val}\n\n"
        "Use the keypad below to enter amount or type directly in chat.\n\n"
        "Min: 💸 ₹1.00 | Max: 💸 ₹50,000.00"
    )
    await query.edit_message_text(text, parse_mode="HTML", reply_markup=build_keypad_keyboard())

async def keypad_confirm_callback(update, context):
    query = update.callback_query
    await query.answer()

    amt_str = context.user_data.get('custom_amount_str', "0")
    if not amt_str or int(amt_str) <= 0:
        await query.answer("Please enter an amount greater than ₹0!", show_alert=True)
        return

    amount = int(amt_str)
    await show_gateway_selection(query, amount)

# Chat text direct type karne ke liye
async def handle_text_input(update, context):
    if context.user_data.get('in_keypad_mode'):
        text_input = update.message.text.strip()
        if text_input.isdigit() and int(text_input) > 0:
            context.user_data['custom_amount_str'] = text_input
            context.user_data['in_keypad_mode'] = False
            
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("💳 PAY UPI", callback_data=f"gateway_upi_{text_input}")],
                [InlineKeyboardButton("➡️ Cancel Request", callback_data="add_balance")]
            ])
            text = (
                "<b>💥 SELECT GATEWAY MODE 💥</b>\n\n"
                f"Deposit Amount: 💸 ₹{text_input}.00"
            )
            await update.message.reply_text(text, parse_mode="HTML", reply_markup=keyboard)

# --- 3. GATEWAY SELECTION ---
async def show_gateway_selection(query, amount):
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("💳 PAY UPI", callback_data=f"gateway_upi_{amount}")],
        [InlineKeyboardButton("➡️ Cancel Request", callback_data="add_balance")]
    ])

    text = (
        "<b>💥 SELECT GATEWAY MODE 💥</b>\n\n"
        f"Deposit Amount: 💸 ₹{amount}.00"
    )
    await query.edit_message_text(text, parse_mode="HTML", reply_markup=keyboard)

async def preset_amount_callback(update, context):
    query = update.callback_query
    await query.answer()
    amount = query.data.split("_")[1]
    await show_gateway_selection(query, amount)

# --- 4. FINAL DYNAMIC QR SCREEN ---
async def show_qr_screen(update, context):
    query = update.callback_query
    await query.answer()

    amount = query.data.split("_")[2]
    qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=300x300&data=upi://pay?pa={UPI_ID}%26pn=RIAZ99%26am={amount}%26cu=INR"

    pay_keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("💸 VERIFY PAYMENT", url="https://t.me/riaz_zayn")],
        [InlineKeyboardButton("➡️ Cancel Order", callback_data="main_menu")]
    ])

    text = (
        f'<a href="{qr_url}">&#8203;</a>'
        "<b>💥 RIAZ 99 STORE — UPI QR ACTIVE 💥</b>\n\n"
        "Merchant Name: RIAZ 99 STORE\n\n"
        f"Scan & pay exactly 💸 ₹{amount}.00\n\n"
        "Tap verify below after completing payment.\n\n"
        "<i>💥 Session expires in 5 minutes. 💥</i>"
    )
    preview_options = LinkPreviewOptions(is_disabled=False, url=qr_url, prefer_large_media=True)
    await query.edit_message_text(text, parse_mode="HTML", reply_markup=pay_keyboard, link_preview_options=preview_options)

# --- OTHER HANDLERS ---
async def placeholder_callback(update, context):
    query = update.callback_query
    await query.answer()

    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("➡️ Back to Menu", callback_data="main_menu")]])
    await query.edit_message_text("<b>Contact Admin @riaz_zayn for this section.</b>", parse_mode="HTML", reply_markup=keyboard)

# --- Execution Entry Point ---
if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()

    TOKEN = os.environ.get("BOT_TOKEN")
    if not TOKEN:
        print("Error: BOT_TOKEN not found!")
        exit(1)

    app_bot = ApplicationBuilder().token(TOKEN).build()

    app_bot.add_handler(CommandHandler("start", main_menu))
    app_bot.add_handler(CallbackQueryHandler(main_menu, pattern="^main_menu$"))
    app_bot.add_handler(CallbackQueryHandler(add_balance_callback, pattern="^add_balance$"))
    app_bot.add_handler(CallbackQueryHandler(keypad_open_callback, pattern="^keypad_open$"))
    app_bot.add_handler(CallbackQueryHandler(keypad_press_callback, pattern="^kp_[0-9|clear|back]"))
    app_bot.add_handler(CallbackQueryHandler(keypad_confirm_callback, pattern="^kp_confirm$"))
    app_bot.add_handler(CallbackQueryHandler(preset_amount_callback, pattern="^amt_"))
    app_bot.add_handler(CallbackQueryHandler(show_qr_screen, pattern="^gateway_upi_"))
    
    # Catch-all for support, history, refer, etc.
    app_bot.add_handler(CallbackQueryHandler(placeholder_callback, pattern="^(buy_now|check_update|history|refer|how_to_use|support|daily_gift)$"))
    
    # Text input for direct numbers
    app_bot.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_input))

    print("Bot is polling...")
    app_bot.run_polling()
