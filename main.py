import time
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, LinkPreviewOptions

BANNER_URL = "https://files.catbox.moe/itqjoi.jpg"

def get_main_menu_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🛒 Buy Now (Products & Panels)", callback_data="buy_now", style="success")],
        [InlineKeyboardButton("📜 Deposit + Key History", callback_data="history")],
        [InlineKeyboardButton("💳 Add Balance (₹)", callback_data="add_balance", style="success"), InlineKeyboardButton("❓ How To Use (Video Tutorial)", callback_data="how_to_use")],
        [InlineKeyboardButton("💬 Support (Admin)", callback_data="support", style="danger")]
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
        [InlineKeyboardButton("✈️ Telegram Support", url="https://t.me/your_username")],
        [InlineKeyboardButton("📸 Instagram", url="https://instagram.com/your_handle"), InlineKeyboardButton("💬 WhatsApp", url="https://wa.me/your_number")],
        [InlineKeyboardButton("⬅️ Back to Main Menu", callback_data="main_menu", style="danger")]
    ])

    text = (
        "<b>📞 RIAZ 99 OFFICIAL SUPPORT</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "<i>If you face any payment or key issues, contact us directly through the links below:</i>"
    )
    await query.edit_message_text(text, parse_mode="HTML", reply_markup=support_keyboard)

async def history_callback(update, context):
    query = update.callback_query
    await query.answer()

    history_keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📥 Deposit History", callback_data="view_deposits"), InlineKeyboardButton("🔑 Key History", callback_data="view_keys")],
        [InlineKeyboardButton("⬅️ Back to Main Menu", callback_data="main_menu", style="danger")]
    ])

    text = (
        "<b>📜 YOUR ACCOUNT HISTORY</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "<i>Select which history you want to check:</i>"
    )
    await query.edit_message_text(text, parse_mode="HTML", reply_markup=history_keyboard)
    
