import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from telegram.ext import (
    ApplicationBuilder, ConversationHandler,
    CommandHandler, MessageHandler, filters, CallbackQueryHandler
)
from bot.views import (
    start, choose_action, get_company, get_title, get_salary, get_location,
    get_requirements, get_contact, get_telegram, get_appeal_time,
    get_responsible_person, get_working_hours, confirm, cancel,
    pagination_handler,
    COMPANY, TITLE, SALARY, LOCATION, REQUIREMENTS, CONTACT,
    TELEGRAM_USERNAME, APPEAL_TIME, RESPONSIBLE_PERSON, WORKING_HOURS, CONFIRM,
    CHOOSING, VIEWING
)

from warnings import filterwarnings
from telegram.warnings import PTBUserWarning

filterwarnings(action="ignore", message=r".*CallbackQueryHandler", category=PTBUserWarning)

TOKEN = "7695753094:AAEqBBsZkfB38atTi03XLWP30oYdDlAkg9E"

app = ApplicationBuilder().token(TOKEN).build()

conv_handler = ConversationHandler(
    entry_points=[CommandHandler('start', start)],
    states={
        CHOOSING: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, choose_action)
        ],
        COMPANY: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_company)],
        TITLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_title)],
        SALARY: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_salary)],
        LOCATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_location)],
        REQUIREMENTS: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_requirements)],
        CONTACT: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_contact)],
        TELEGRAM_USERNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_telegram)],
        APPEAL_TIME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_appeal_time)],
        RESPONSIBLE_PERSON: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_responsible_person)],
        WORKING_HOURS: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_working_hours)],
        CONFIRM: [MessageHandler(filters.Regex('^(✅ Ha|❌ Yo‘q)$'), confirm)],
        VIEWING: [CallbackQueryHandler(pagination_handler, pattern=r'^page_\d+$')]
    },
    fallbacks=[CommandHandler('cancel', cancel)],
)

app.add_handler(conv_handler)

if __name__ == "__main__":
    print("Bot ishga tushdi...")
    app.run_polling()
