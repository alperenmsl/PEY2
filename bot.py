from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, ParseMode, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler

# Admin und Gruppe
ADMIN_CHAT_ID = 6751658116
GROUP_CHAT_ID = -4988709403  # Private Gruppe Chat-ID

# States
CHOOSE_PLATFORM, CHOOSE_ITEM, ENTER_AMOUNT, UPLOAD_PROOF = range(4)

# /start
def start(update, context):
    try:
        with open(r"assets\Service.gif", "rb") as gif_file:
            update.message.reply_animation(
                animation=gif_file,
                caption="🚀 Welcome to *Pey2 Panel Bot*! Boost your social media fast and easy!",
                parse_mode=ParseMode.MARKDOWN
            )
    except Exception as e:
        # Fallback Bild
        with open(r"assets\BlackOnWhite.png", "rb") as img_file:
            update.message.reply_photo(
                photo=img_file,
                caption="🚀 Welcome to *Pey2 Panel Bot*! Boost your social media fast and easy!",
                parse_mode=ParseMode.MARKDOWN
            )



    # Buttons
    update.message.reply_text(
        "Choose an option:",
        reply_markup=ReplyKeyboardMarkup([
            ["📋 Services"],
            ["🌐 Social Media", "📞 Contact Support"],
            ["ℹ️ Order Info"]
        ], one_time_keyboard=True, resize_keyboard=True)
    )

# Services Menü
def services(update, context):
    update.message.reply_text(
        "📌 Choose a platform to boost:",
        reply_markup=ReplyKeyboardMarkup([
            ["Instagram", "TikTok"],
            ["⬅️ Back"]
        ], one_time_keyboard=True, resize_keyboard=True)
    )
    return CHOOSE_PLATFORM





# Plattform auswählen → Preisliste + Auswahl
def choose_platform(update, context):
    platform_text = update.message.text.strip().lower()  # entfernt führende/abschließende Leerzeichen
    context.user_data['platform'] = platform_text

    if "instagram" in platform_text:
        text = (
            "📸 *Instagram Followers - 4€/1000*\n"
            "🔝 Quality: High Quality / Real\n"
            "⌛ Start: 0-1h\n"
            "⚡ Speed: Up To 15K/Hour\n"
            "♻️ Refill: No Refill / 0-2%\n"
            "⬇️ Minimum: 100\n"
            "⬆️ Maximum: 500,000"
        )
    elif "tiktok" in platform_text:
        text = (
            "🎵 *TikTok Followers - 6€/1000*\n"
            "🔝 Quality: High Quality\n"
            "⌛ Start: 0-1h\n"
            "⚡ Speed: 100K/Day\n"
            "♻️ Refill: 30 Days\n"
            "⬇️ Minimum: 100\n"
            "⬆️ Maximum: 500,000"
        )
    elif "back" in platform_text:
        return services(update, context)
    else:
        update.message.reply_text("❌ Invalid platform!")
        return CHOOSE_PLATFORM

    # Preisliste anzeigen
    update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)
    # Danach fragen, was gekauft werden soll
    update.message.reply_text(
        "What do you want to buy?",
        reply_markup=ReplyKeyboardMarkup([
            ["Followers", "Likes", "Views", "Share"],
            ["⬅️ Cancel"]
        ], one_time_keyboard=True, resize_keyboard=True)
    )
    return CHOOSE_ITEM


    # Preisliste anzeigen
    update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)

    # Danach fragen, was gekauft werden soll
    update.message.reply_text(
        "What do you want to buy?",
        reply_markup=ReplyKeyboardMarkup([
            ["Followers", "Likes", "Views", "Share"],
            ["⬅️ Cancel"]
        ], one_time_keyboard=True, resize_keyboard=True)
    )
    return CHOOSE_ITEM

# Service auswählen
def choose_item(update, context):
    item = update.message.text.strip().lower()
    context.user_data['item'] = item

    if item not in ["followers", "likes", "views", "share"]:
        update.message.reply_text("❌ Please choose a valid option!")
        return CHOOSE_ITEM

    update.message.reply_text(f"✏️ How many {item.capitalize()} do you want to buy?", reply_markup=ReplyKeyboardRemove())
    return ENTER_AMOUNT

# Menge eingeben & Preis berechnen
def enter_amount(update, context):
    try:
        amount = int(update.message.text.strip())

        # Check auf gültigen Bereich
        if amount <= 0:
            update.message.reply_text("❌ You must enter a number greater than 0!")
            return ENTER_AMOUNT
        if amount > 500_000:
            update.message.reply_text("❌ Maximum allowed is 500,000! Please enter a lower amount.")
            return ENTER_AMOUNT

        context.user_data['amount'] = amount
        platform = context.user_data['platform']
        item = context.user_data['item']

        # Preisberechnung
        if platform == "instagram" and item == "followers":
            price = (amount / 1000) * 4
        elif platform == "tiktok" and item == "followers":
            price = (amount / 1000) * 6
        else:
            price = 0  # Likes, Views, Share optional erweitern

        context.user_data['price'] = price

        update.message.reply_text(
            f"✅ *Order Summary*\nPlatform: {platform.capitalize()}\n"
            f"Service: {item.capitalize()}\nAmount: {amount}\nTotal: {price}€\n\n"
            f"💸 Send the payment to PayPal: pey2@service.com\n"
            "📷 After payment, upload a screenshot as proof.",
            parse_mode=ParseMode.MARKDOWN
        )
        return UPLOAD_PROOF

    except ValueError:
        update.message.reply_text("❌ Please enter a valid number!")
        return ENTER_AMOUNT



# Payment Proof hochladen
def upload_proof(update, context):
    if update.message.photo:
        # Proof an Admin weiterleiten
        update.message.forward(chat_id=ADMIN_CHAT_ID)
        # Proof an private Gruppe weiterleiten
        update.message.forward(chat_id=GROUP_CHAT_ID)

        # Order-Details an Gruppe
        context_text = (
            f"📌 New Order\n"
            f"User: @{update.message.from_user.username}\n"
            f"Platform: {context.user_data['platform']}\n"
            f"Service: {context.user_data['item']}\n"
            f"Amount: {context.user_data['amount']}\n"
            f"Total: {context.user_data['price']}€"
        )
        context.bot.send_message(chat_id=GROUP_CHAT_ID, text=context_text)

        # Dankes-Nachricht an User + zurück zum Start
        update.message.reply_text(
            "✅ Thanks for your Order. Payment proof received. Your order is being processed."
        )
        start(update, context)
        return ConversationHandler.END
    else:
        update.message.reply_text("❌ Please upload a photo as proof of payment.")
        return UPLOAD_PROOF

# Andere Commands
def contact_support(update, context):
    update.message.reply_text("📞 If you have any questions or problems, please contact @alperenm38")

def social_media(update, context):
    keyboard = [
        [InlineKeyboardButton("🟧 Instagram", url="https://instagram.com/Pey2")],
        [InlineKeyboardButton("🟪 TikTok", url="https://tiktok.com/@Pey2_TikTok")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text(
        "🌐 Our Social Media:",
        reply_markup=reply_markup
    )

def order_info(update, context):
    update.message.reply_text("ℹ️ Order Info coming soon!")

def cancel(update, context):
    update.message.reply_text("❌ Operation cancelled.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

# Main
def main():
    updater = Updater("8336579553:AAFeLtqBdQ138xKtb1hkZY8_QZ6l0MGSq0k", use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.regex("🌐 Social Media"), social_media))
    dp.add_handler(MessageHandler(Filters.regex("📞 Contact Support"), contact_support))
    dp.add_handler(MessageHandler(Filters.regex("ℹ️ Order Info"), order_info))

    # Conversation Handler für Services Flow
    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(Filters.regex("📋 Services"), services)],
        states={
            CHOOSE_PLATFORM: [MessageHandler(Filters.text & ~Filters.command, choose_platform)],
            CHOOSE_ITEM: [MessageHandler(Filters.text & ~Filters.command, choose_item)],
            ENTER_AMOUNT: [MessageHandler(Filters.text & ~Filters.command, enter_amount)],
            UPLOAD_PROOF: [MessageHandler(Filters.photo, upload_proof)]
        },
        fallbacks=[MessageHandler(Filters.regex("⬅️ Cancel"), cancel)]
    )
    dp.add_handler(conv_handler)

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()

