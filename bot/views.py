from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    ApplicationBuilder, CommandHandler, ContextTypes,
    MessageHandler, filters, ConversationHandler
)
import django
import os
import sys
from pathlib import Path
from asgiref.sync import sync_to_async

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from bot.models import Vacancy

CHOOSING, COMPANY, TITLE, SALARY, LOCATION, REQUIREMENTS, CONTACT, CONFIRM, SEARCHING_VACANCY, SEARCH_RESULTS = range(10)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["📝 Vakansiya joylash", "🔍 Vakansiya qidirish"]]
    await update.message.reply_text(
        "Xush kelibsiz! Iltimos kerakli bo‘limni tanlang:",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )
    return CHOOSING

async def choose_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "📝 Vakansiya joylash":
        await update.message.reply_text("Kompaniya nomini kiriting:", reply_markup=ReplyKeyboardRemove())
        context.user_data['vacancy'] = {}
        return COMPANY
    elif text == "🔍 Vakansiya qidirish":
        await update.message.reply_text("Qaysi pozitsiyada ish qidiryapsiz?", reply_markup=ReplyKeyboardRemove())
        return SEARCHING_VACANCY
    else:
        await update.message.reply_text("Iltimos, menyudan tanlang.")
        return CHOOSING

async def get_company(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['vacancy']['company_name'] = update.message.text
    await update.message.reply_text("Vakansiya nomini kiriting:")
    return TITLE

async def get_title(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['vacancy']['title'] = update.message.text
    await update.message.reply_text("Ish haqini kiriting:")
    return SALARY

async def get_salary(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['vacancy']['salary'] = update.message.text
    await update.message.reply_text("Lokatsiyani kiriting:")
    return LOCATION

async def get_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['vacancy']['location'] = update.message.text
    await update.message.reply_text("Talablarni kiriting:")
    return REQUIREMENTS

async def get_requirements(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['vacancy']['requirements'] = update.message.text
    await update.message.reply_text("Aloqa ma’lumotlarini kiriting:")
    return CONTACT

async def get_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['vacancy']['contact_info'] = update.message.text

    data = context.user_data['vacancy']
    text = (
        f"📋 *Vakansiya tafsilotlari:*\n"
        f"🏢 Kompaniya: {data['company_name']}\n"
        f"💼 Lavozim: {data['title']}\n"
        f"💰 Ish haqi: {data['salary']}\n"
        f"📍 Lokatsiya: {data['location']}\n"
        f"🧾 Talablar: {data['requirements']}\n"
        f"📞 Aloqa: {data['contact_info']}\n\n"
        f"Tasdiqlaysizmi?"
    )
    keyboard = [["✅ Ha", "❌ Yo‘q"]]
    await update.message.reply_text(text, parse_mode="Markdown", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))
    return CONFIRM

@sync_to_async
def create_vacancy(data):
    return Vacancy.objects.create(**data)

async def confirm_submission(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "✅ Ha":
        data = context.user_data['vacancy']
        await create_vacancy(data)  # sync_to_async orqali chaqiryapmiz
        await update.message.reply_text("✅ Vakansiya muvaffaqiyatli yuborildi! Admin tasdiqlashi kutilmoqda.", reply_markup=ReplyKeyboardRemove())
    else:
        await update.message.reply_text("❌ Bekor qilindi.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

@sync_to_async
def search_vacancies(title):
    return list(Vacancy.objects.filter(title__icontains=title).values("company_name", "title", "salary", "location", "requirements", "contact_info"))

async def search_vacancy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text
    results = await search_vacancies(query)

    if not results:
        await update.message.reply_text("Vakansiya topilmadi.")
        return ConversationHandler.END

    text = "🔎 Topilgan vakansiyalar:\n\n"
    for vac in results:
        text += (f"🏢 {vac['company_name']}\n💼 {vac['title']}\n💰 {vac['salary']}\n📍 {vac['location']}\n"
                 f"🧾 {vac['requirements']}\n📞 {vac['contact_info']}\n\n")

    await update.message.reply_text(text)
    return ConversationHandler.END

conv_handler = ConversationHandler(
    entry_points=[CommandHandler("start", start)],
    states={
        CHOOSING: [MessageHandler(filters.TEXT & ~filters.COMMAND, choose_action)],
        COMPANY: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_company)],
        TITLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_title)],
        SALARY: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_salary)],
        LOCATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_location)],
        REQUIREMENTS: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_requirements)],
        CONTACT: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_contact)],
        CONFIRM: [MessageHandler(filters.Regex("^(✅ Ha|❌ Yo‘q)$"), confirm_submission)],
        SEARCHING_VACANCY: [MessageHandler(filters.TEXT & ~filters.COMMAND, search_vacancy)],
    },
    fallbacks=[]
)

if __name__ == "__main__":
    application = ApplicationBuilder().token("7695753094:AAEqBBsZkfB38atTi03XLWP30oYdDlAkg9E").build()
    application.add_handler(conv_handler)
    application.run_polling()
