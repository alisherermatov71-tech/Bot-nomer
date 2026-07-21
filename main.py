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

# Logging орнату
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# --- БАПТАУЛАР (CONFIGURATION) ---
TOKEN = "8811948718:AAGHcgdmjPP9789n99-Lf21qMjRFw8wdXVQ"
ADMIN_ID = 123456789  # Сіздің Telegram ID-іңіз

# TOPSMM API баптаулары
SMM_API_URL = "https://topsmm.uz/api/v2"
SMM_API_KEY = "7d2810d221d86fd2b1c5ff79e4a85c69"

# Деректерді сақтауға арналған уақытша жад
USER_BALANCES = {}  # {user_id: balance}
USER_STATES = {}    # {user_id: state}

# --- SMM API ФУНКЦИЯЛАРЫ ---
def api_create_order(service_id, link, quantity):
    payload = {
        'key': SMM_API_KEY,
        'action': 'add',
        'service': service_id,
        'link': link,
        'quantity': quantity
    }
    try:
        response = requests.post(SMM_API_URL, data=payload)
        return response.json()
    except Exception as e:
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
        [InlineKeyboardButton("🎵 TikTok Қаралым (ID: 101)", callback_data="cat_tiktok_view")],
        [InlineKeyboardButton("❤️ TikTok Лайк (ID: 102)", callback_data="cat_tiktok_like")],
        [InlineKeyboardButton("📸 Instagram Жазылушы (ID: 201)", callback_data="cat_insta_sub")],
        [InlineKeyboardButton("◀️ Басты мәзір", callback_data="back_main")]
    ]
    return InlineKeyboardMarkup(keyboard)

# --- HANDLER-ЛЕР ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user.id not in USER_BALANCES:
        USER_BALANCES[user.id] = 0.0  # Бастапқы баланс
        
    text = (
        f"Сәлем, {user.first_name}! 👋

"
        "🔥 Бұл автоматты SMM накрутка боты.
"
        "Балансыңызды толтырып, бірден TikTok және Instagram қызметтерін автоматты түрде сатып алыңыз!

"
        "Мәзірден қажетті бөлімді таңдаңыз:"
    )
    if update.message:
        await update.message.reply_text(text, reply_markup=main_menu())
    elif update.callback_query:
        await update.callback_query.message.edit_text(text, reply_markup=main_menu())

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    user_id = query.from_user.id

    if data == "buy_smm":
        await query.message.edit_text(
            "📦 **Қызмет түрін таңдаңыз:**
"
            "Әр қызметтің автоматты түрде өңделуі үшін балансыңызда жеткілікті теңге болуы керек.",
            parse_mode="Markdown",
            reply_markup=smm_categories_menu()
        )

    elif data in ["cat_tiktok_view", "cat_tiktok_like", "cat_insta_sub"]:
        service_map = {
            "cat_tiktok_view": {"id": 101, "name": "TikTok Қаралым", "price": 0.5},
            "cat_tiktok_like": {"id": 102, "name": "TikTok Лайк", "price": 1.5},
            "cat_insta_sub": {"id": 201, "name": "Instagram Жазылушы", "price": 3.0}
        }
        selected = service_map.get(data)
        USER_STATES[user_id] = {"state": "waiting_order", "service_id": selected["id"], "price": selected["price"], "name": selected["name"]}
        
        await query.message.edit_text(
            f"🛒 **{selected['name']}** таңдалды.
"
            f"💰 Бағасы: 1 данасы — {selected['price']} ₸

"
            "🔗 Енді маған **Сілтеме мен санын** бір жолға жазып жіберіңіз.
"
            "Мысалы: `https://tiktok.com/@user/video/123 1000`",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("◀️ Артқа", callback_data="buy_smm")]])
        )

    elif data == "profile":
        balance = USER_BALANCES.get(user_id, 0.0)
        text = (
            "👤 **Сіздің жеке кабинетіңіз:**

"
            f"🆔 ID: `{user_id}`
"
            f"💰 Балансыңыз: `{balance} ₸`
"
            "📦 Статус: Белсенді клиент"
        )
        await query.message.edit_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("◀️ Артқа", callback_data="back_main")]]))

    elif data == "top_up":
        text = (
            "💳 **Балансты толтыру (Kaspi / Halyk):**

"
            "Аударым жасау үшін реквизит:
"
            "💳 `4400 4300 1234 5678` (Жания Р.)

"
            "⚠️ Ақшаны аударған соң скриншотты және өз ID-іңізді админге жіберіңіз: @admin_username
"
            "Админ балансыңызды автоматты/қолмен толтырады."
        )
        await query.message.edit_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("◀️ Басты мәзірге", callback_data="back_main")]]))

    elif data == "referral":
        bot_username = context.bot.username if context.bot else "bot"
        ref_link = f"https://t.me/{bot_username}?start=ref_{user_id}"
        text = (
            "👥 **Рефералды жүйе:**

"
            "Достарыңызды шақырыңыз және олардың толтырған балансынан пайыз алыңыз!

"
            f"🔗 Сіздің сілтемеңіз:
`{ref_link}`"
        )
        await query.message.edit_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("◀️ Артқа", callback_data="back_main")]]))

    elif data == "support":
        await query.message.edit_text(
            "📞 **Қолдау қызметі:**

"
            "Сұрақтар бойынша хабарласыңыз: @admin_username",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("◀️ Артқа", callback_data="back_main")]]))

    elif data == "back_main":
        if user_id in USER_STATES:
            del USER_STATES[user_id]
        await start(update, context)

# --- МӘТІНДІК ХАБАРЛАМАЛАРДЫ ӨҢДЕУ ---
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip()

    if user_id in USER_STATES and USER_STATES[user_id]["state"] == "waiting_order":
        state_data = USER_STATES[user_id]
        parts = text.split()
        
        if len(parts) < 2:
            await update.message.reply_text("❌ Қате формат! Сілтеме мен санын қатар жазыңыз.
Мысалы: `https://link.com 500`", parse_mode="Markdown")
            return
            
        link = parts[0]
        try:
            quantity = int(parts[1])
        except ValueError:
            await update.message.reply_text("❌ Сан дұрыс көрсетілмеді. Тек санды жазыңыз.")
            return

        total_price = quantity * state_data["price"]
        current_balance = USER_BALANCES.get(user_id, 0.0)

        if current_balance < total_price:
            await update.message.reply_text(
                f"❌ **Балансыңыз жеткіліксіз!**
"
                f"Қажет сома: {total_price} ₸
"
                f"Сіздің баланс: {current_balance} ₸

"
                "Алдымен балансты толтырыңыз!",
                parse_mode="Markdown"
            )
            return

        # TopSMM API арқылы тапсырысты жіберу
        await update.message.reply_text("⏳ Тапсырысыңыз өңделуде, TopSMM серверге жіберілуде...")
        res = api_create_order(state_data["service_id"], link, quantity)

        if "order" in res:
            USER_BALANCES[user_id] -= total_price
            order_id = res["order"]
            await update.message.reply_text(
                f"✅ **Тапсырыс сәтті қабылданды!**

"
                f"🆔 Тапсырыс ID: `{order_id}`
"
                f"📦 Қызмет: {state_data['name']}
"
                f"🔗 Сілтеме: {link}
"
                f"📊 Саны: {quantity}
"
                f"💸 Шығын: {total_price} ₸

"
                f"💰 Қалған баланс: `{USER_BALANCES[user_id]} ₸`",
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🚀 Жаңа тапсырыс", callback_data="buy_smm"), InlineKeyboardButton("🏠 Басты мәзір", callback_data="back_main")]]))
        else:
            await update.message.reply_text(f"❌ Қате орын алды немесе API жауап бермеді: {res}")
            
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
