import os
import logging
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters
)

# Logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# --- БАСПТАУЛАР ---
TOKEN = "8811948718:AAGHcgdmjPP9789n99-Lf21qMjRFw8wdXVQ" # >>> БҰЛДЫ @BotFather-тан жаңасын ал!
ADMIN_ID = 123456789 # >>> БҰЛДЫ @userinfobot-тан өзіңнің ID-ңды қой!

SMM_API_URL = "https://topsmm.uz/api/v2"
SMM_API_KEY = "7d2810d221d86fd2b1c5ff79e4a85c69" # >>> БҰЛДЫ topsmm.uz-тан жаңасын ал!

USER_BALANCES = {}
USER_STATES = {}

# --- SMM API ---
def api_create_order(service_id, link, quantity):
    payload = {
        'key': SMM_API_KEY,
        'action': 'add',
        'service': service_id,
        'link': link,
        'quantity': quantity
    }
    try:
        response = requests.post(SMM_API_URL, data=payload, timeout=15)
        return response.json()
    except Exception as e:
        logging.error(f"API Error: {e}")
        return {'error': str(e)}

# --- МӘЗІРЛЕР ---
def main_menu():
    keyboard = [
        [InlineKeyboardButton("🚀 Накрутка сатып алу", callback_data="buy_smm")],
        [InlineKeyboardButton("👤 Жеке кабинет", callback_data="profile"),
         InlineKeyboardButton("💳 Баланс толтыру", callback_data="top_up")],
        [InlineKeyboardButton("👥 Реферал", callback_data="referral"),
         InlineKeyboardButton("📞 Қолдау", callback_data="support")]
    ]
    return InlineKeyboardMarkup(keyboard)

def smm_categories_menu():
    keyboard = [
        [InlineKeyboardButton("🎵 TikTok Қаралым", callback_data="cat_tiktok_view")],
        [InlineKeyboardButton("❤️ TikTok Лайк", callback_data="cat_tiktok_like")],
        [InlineKeyboardButton("📸 Instagram Жазылушы", callback_data="cat_insta_sub")],
        [InlineKeyboardButton("◀️ Басты мәзір", callback_data="back_main")]
    ]
    return InlineKeyboardMarkup(keyboard)

# --- HANDLER-ЛЕР ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user.id not in USER_BALANCES:
        USER_BALANCES[user.id] = 0.0

    text = (
        f"Сәлем, {user.first_name}! 👋\n\n"
        "🔥 Бұл автоматты SMM накрутка боты.\n"
        "Балансыңызды толтырып, бірден TikTok және Instagram қызметтерін сатып алыңыз!\n\n"
        "Мәзірден қажетті бөлімді таңдаңыз:"
    )

    if update.message:
        await update.message.reply_text(text, reply_markup=main_menu())
    elif update.callback_query:
        await update.callback_query.edit_message_text(text, reply_markup=main_menu())

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    user_id = query.from_user.id

    if data == "buy_smm":
        await query.edit_message_text(
            "📦 **Қызмет түрін таңдаңыз:**\nӘр қызмет үшін балансыңызда жеткілікті теңге болуы керек.",
            parse_mode="Markdown",
            reply_markup=smm_categories_menu()
        )

    elif data in ["cat_tiktok_view", "cat_tiktok_like", "cat_insta_sub"]:
        service_map = {
            "cat_tiktok_view": {"id": 101, "name": "TikTok Қаралым", "price": 0.5},
            "cat_tiktok_like": {"id": 102, "name": "TikTok Лайк", "price": 1.5},
            "cat_insta_sub": {"id": 201, "name": "Instagram Жазылушы", "price": 3.0}
        }
        selected = service_map[data]
        USER_STATES[user_id] = {"state": "waiting_order", "service_id": selected["id"], "price": selected["price"], "name": selected["name"]}

        await query.edit_message_text(
            f"🛒 **{selected['name']}** таңдалды.\n"
            f"💰 Бағасы: 1 данасы — {selected['price']} ₸\n\n"
            "🔗 Енді маған **Сілтеме мен санын** бір жолға жібер.\n"
            "Мысалы: `https://tiktok.com/@user/video/123 1000`",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("◀️ Артқа", callback_data="buy_smm")]])
        )

    elif data == "profile":
        balance = USER_BALANCES.get(user_id, 0.0)
        text = (
            f"👤 **Сіздің жеке кабинетіңіз:**\n\n"
            f"🆔 ID: `{user_id}`\n"
            f"💰 Балансыңыз: `{balance} ₸`\n"
            "📦 Статус: Белсенді клиент"
        )
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("◀️ Артқа", callback_data="back_main")]]))

    elif data == "top_up":
        text = (
            "💳 **Балансты толтыру (Kaspi / Halyk):**\n\n"
            "Аударым реквизит:\n"
            "💳 `4400 4300 1234 5678` (Жания Р.)\n\n"
            "⚠️ Ақшаны аударған соң скриншотты және өз ID-іңізді админге жіберіңіз."
        )
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("◀️ Басты мәзірге", callback_data="back_main")]]))

    elif data == "referral":
        bot_username = context.bot.username
        ref_link = f"https://t.me/{bot_username}?start=ref_{user_id}"
        text = (
            "👥 **Рефералды жүйе:**\n\n"
            "Достарыңызды шақырыңыз!\n\n"
            f"🔗 Сіздің сілтемеңіз:\n`{ref_link}`"
        )
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("◀️ Артқа", callback_data="back_main")]]))

    elif data == "support":
        await query.edit_message_text(
            "📞 **Қолдау қызметі:**\n\nСұрақтар бойынша админге жазыңыз.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("◀️ Артқа", callback_data="back_main")]])
        )

    elif data == "back_main":
        if user_id in USER_STATES:
            del USER_STATES[user_id]
        await start(update, context)

# --- МӘТІНДІ ӨҢДЕУ ---
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return
    user_id = update.effective_user.id
    text = update.message.text.strip()

    if user_id in USER_STATES and USER_STATES[user_id]["state"] == "waiting_order":
        state_data = USER_STATES[user_id]
        parts = text.split()

        if len(parts) < 2:
            await update.message.reply_text("❌ Қате формат! Сілтеме мен санын қатар жазыңыз.\nМысалы: `https://link.com 500`", parse_mode="Markdown")
            return

        link, qty_str = parts[0], parts[1]
        try:
            quantity = int(qty_str)
        except:
            await update.message.reply_text("❌ Сан дұрыс емес.")
            return

        total_price = quantity * state_data["price"]
        current_balance = USER_BALANCES.get(user_id, 0.0)

        if current_balance < total_price:
            await update.message.reply_text(f"❌ **Балансыңыз жеткіліксіз!**\nҚажет: {total_price} ₸\nСізде: {current_balance} ₸", parse_mode="Markdown")
            return

        await update.message.reply_text("⏳ Тапсырысыңыз өңделуде...")
        res = api_create_order(state_data["service_id"], link, quantity)

        if "order" in res:
            USER_BALANCES[user_id] -= total_price
            await update.message.reply_text(
                f"✅ **Тапсырыс қабылданды!**\n\n"
                f"🆔 ID: `{res['order']}`\n"
                f"📦 {state_data['name']}\n"
                f"💸 Шығын: {total_price} ₸\n"
                f"💰 Қалдық: `{USER_BALANCES[user_id]} ₸`",
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🚀 Жаңа тапсырыс", callback_data="buy_smm")]])
            )
        else:
            await update.message.reply_text(f"❌ API қате: {res}")

        del USER_STATES[user_id]

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("TopSMM Bot іске қосылды!")
    app.run_polling()

if __name__ == "__main__":
    main()
