from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler

from config.settings import GROUP_IDS
from .models import Vacancy
from django.core.paginator import Paginator
from asgiref.sync import sync_to_async

(
    CHOOSING,
    COMPANY, TITLE, SALARY, LOCATION, REQUIREMENTS,
    CONTACT, TELEGRAM_USERNAME, APPEAL_TIME,
    RESPONSIBLE_PERSON, WORKING_HOURS, CONFIRM,
    VIEWING
) = range(13)


async def main_menu(update: Update):
    keyboard = [
        ["Vakansiya qo'shish", "Vakansiyalarni ko'rish"],
        ["Tugatish"]
    ]
    await update.message.reply_text(
        "Iltimos, tanlang:",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    )
    return CHOOSING


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return await main_menu(update)


async def choose_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "Vakansiyalarni ko'rish":
        return await show_vacancies(update, context, page=1)
    elif text == "Vakansiya qo'shish":
        await update.message.reply_text("Iltimos, idorangiz nomini kiriting:")
        context.user_data['vacancy'] = {}
        return COMPANY
    elif text == "Tugatish":
        await update.message.reply_text("Suhbat yakunlandi. Rahmat!")
        return ConversationHandler.END
    else:
        await update.message.reply_text("Iltimos, faqat menyudan tanlang.")
        return CHOOSING


@sync_to_async
def get_vacancies_page(page):
    vacancies = Vacancy.objects.order_by('-created_at').all()
    paginator = Paginator(vacancies, 5)
    if page > paginator.num_pages:
        page = paginator.num_pages
    if page < 1:
        page = 1
    page_obj = paginator.page(page)
    vacancy_list = list(page_obj.object_list)
    return vacancy_list, paginator.num_pages


async def show_vacancies(update: Update, context: ContextTypes.DEFAULT_TYPE, page=1):
    vacancies, num_pages = await get_vacancies_page(page)

    if not vacancies:
        await update.message.reply_text("Hozircha vakansiyalar mavjud emas.")
        return await main_menu(update)

    text = "*Vakansiyalar ro‘yxati:*\n\n"
    for v in vacancies:
        text += (
            f"🏢 *{v.company_name}*\n"
            f"💼 {v.title}\n"
            f"💰 {v.salary}\n"
            f"📍 {v.location}\n"
            f"🔧 Talablar: {v.requirements}\n"
            f"📞 Aloqa: {v.contact_info}\n"
            f"📱 Telegram: {v.telegram_username or '-'}\n"
            f"⏰ Murojaat vaqti: {v.appeal_time}\n"
            f"👤 Mas'ul: {v.responsible_person}\n"
            f"🕒 Ish vaqti: {v.working_hours}\n"
            f"-----------------------\n"
        )

    buttons = []
    if page > 1:
        buttons.append(InlineKeyboardButton("⬅️ Oldingi", callback_data=f"page_{page - 1}"))
    if page < num_pages:
        buttons.append(InlineKeyboardButton("Keyingi ➡️", callback_data=f"page_{page + 1}"))

    if buttons:
        # Agar sahifalash tugmalari mavjud bo'lsa, ularni ko'rsatish
        await update.message.reply_text(
            text,
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([buttons])
        )
        return VIEWING  # Sizning konversatsiya holatingiz, o'zgartiring kerak bo'lsa
    else:
        await update.message.reply_text(text, parse_mode="Markdown")
        return await main_menu(update)


async def pagination_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data
    if data.startswith("page_"):
        page = int(data.split("_")[1])
        vacancies, num_pages = await get_vacancies_page(page)

        text = "*Vakansiyalar ro‘yxati:*\n\n"
        for v in vacancies:
            text += (
                f"🏢 *{v.company_name}*\n"
                f"💼 {v.title}\n"
                f"💰 {v.salary}\n"
                f"📍 {v.location}\n"
                f"🔧 Talablar: {v.requirements}\n"
                f"📞 Aloqa: {v.contact_info}\n"
                f"📱 Telegram: {v.telegram_username or '-'}\n"
                f"⏰ Murojaat vaqti: {v.appeal_time}\n"
                f"👤 Mas'ul: {v.responsible_person}\n"
                f"🕒 Ish vaqti: {v.working_hours}\n"
                f"-----------------------\n"
            )

        buttons = []
        if page > 1:
            buttons.append(InlineKeyboardButton("⬅️ Oldingi", callback_data=f"page_{page - 1}"))
        if page < num_pages:
            buttons.append(InlineKeyboardButton("Keyingi ➡️", callback_data=f"page_{page + 1}"))

        await query.edit_message_text(
            text=text,
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([buttons]) if buttons else None
        )
    return VIEWING


async def get_company(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['vacancy']['company_name'] = update.message.text
    await update.message.reply_text("💻 Lavozim nomini kiriting:")
    return TITLE


async def get_title(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['vacancy']['title'] = update.message.text
    await update.message.reply_text("💵 Maoshni kiriting:")
    return SALARY


async def get_salary(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['vacancy']['salary'] = update.message.text
    await update.message.reply_text("🚩 Hududni kiriting:")
    return LOCATION


async def get_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['vacancy']['location'] = update.message.text
    await update.message.reply_text("Talablarni kiriting:")
    return REQUIREMENTS


async def get_requirements(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['vacancy']['requirements'] = update.message.text
    await update.message.reply_text("📞 Aloqa ma'lumotlarini kiriting:")
    return CONTACT


async def get_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['vacancy']['contact_info'] = update.message.text
    await update.message.reply_text("Telegram username kiriting")
    return TELEGRAM_USERNAME


async def get_telegram(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['vacancy']['telegram_username'] = update.message.text
    await update.message.reply_text(
        "⏰ Murojaat qilish mumkin bo‘lgan vaqtni kiriting (masalan, Dushanba-Juma, 9:00-18:00):")
    return APPEAL_TIME


async def get_appeal_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['vacancy']['appeal_time'] = update.message.text
    await update.message.reply_text("👤 Mas'ul shaxsning ismini kiriting:")
    return RESPONSIBLE_PERSON


async def get_responsible_person(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['vacancy']['responsible_person'] = update.message.text
    await update.message.reply_text("🕒 Ish vaqtini kiriting (masalan, Haftaning barcha kunlari, 9:00-18:00):")
    return WORKING_HOURS


async def get_working_hours(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['vacancy']['working_hours'] = update.message.text
    data = context.user_data['vacancy']

    text = (
        f"*Ish e'loni:*\n\n"
        f"🏢 *Idora:* {data['company_name']}\n"
        f"💼 *Lavozim:* {data['title']}\n"
        f"💰 *Maosh:* {data['salary']}\n"
        f"📍 *Hudud:* {data['location']}\n"
        f"🔧 *Talablar:* {data['requirements']}\n"
        f"📞 *Aloqa:* {data['contact_info']}\n"
        f"📱 *Telegram:* {data['telegram_username']}\n"
        f"⏰ *Murojaat vaqti:* {data['appeal_time']}\n"
        f"👤 *Mas'ul:* {data['responsible_person']}\n"
        f"🕒 *Ish vaqti:* {data['working_hours']}\n\n"
        f"✅ Ma'lumotlar to'g'rimi? Tasdiqlaysizmi?"
    )
    keyboard = [["✅ Ha", "❌ Yo‘q"]]
    await update.message.reply_text(
        text,
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    )
    return CONFIRM


@sync_to_async
def save_vacancy(data):
    Vacancy.objects.create(
        company_name=data['company_name'],
        title=data['title'],
        salary=data['salary'],
        location=data['location'],
        requirements=data['requirements'],
        contact_info=data['contact_info'],
        telegram_username=data['telegram_username'] if data['telegram_username'] != '-' else None,
        appeal_time=data['appeal_time'],
        responsible_person=data['responsible_person'],
        working_hours=data['working_hours']
    )


async def send_vacancy_to_groups(context, data):
    from telegram.constants import ParseMode

    text = (
        f"*Yangi vakansiya:*\n\n"
        f"🏢 *Idora:* {data['company_name']}\n"
        f"💼 *Lavozim:* {data['title']}\n"
        f"💰 *Maosh:* {data['salary']}\n"
        f"📍 *Hudud:* {data['location']}\n"
        f"🔧 *Talablar:* {data['requirements']}\n"
        f"📞 *Aloqa:* {data['contact_info']}\n"
        f"📱 *Telegram:* {data['telegram_username']}\n"
        f"⏰ *Murojaat vaqti:* {data['appeal_time']}\n"
        f"👤 *Mas'ul:* {data['responsible_person']}\n"
        f"🕒 *Ish vaqti:* {data['working_hours']}"
    )

    for group_id in GROUP_IDS:
        try:
            await context.bot.send_message(
                chat_id=group_id,
                text=text,
                parse_mode=ParseMode.MARKDOWN
            )
        except Exception as e:
            print(f"Xatolik yuz berdi ({group_id}):", e)

async def confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    answer = update.message.text
    if answer == "✅ Ha":
        data = context.user_data.get('vacancy')
        await save_vacancy(data)
        await send_vacancy_to_groups(context, data)  # Yangi qo'shilgan qadam
        await update.message.reply_text("Vakansiya muvaffaqiyatli joylashtirildi!")
        return await main_menu(update)
    else:
        await update.message.reply_text("Jarayon bekor qilindi. Asosiy menyuga qaytildi.")
        return await main_menu(update)


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Jarayon bekor qilindi.")
    return ConversationHandler.END
