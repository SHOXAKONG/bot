from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Vacancy
import telegram

BOT_TOKEN = '7695753094:AAEqBBsZkfB38atTi03XLWP30oYdDlAkg9E'
CHANNEL_ID = '-4810645155'

bot = telegram.Bot(token=BOT_TOKEN)

@receiver(post_save, sender=Vacancy)
def send_vacancy_to_channel(sender, instance, created, **kwargs):
    if instance.is_confirmed:
        text = (
            f"📢 *Yangi Vakansiya!*\n"
            f"🏢 Kompaniya: {instance.company_name}\n"
            f"💼 Lavozim: {instance.title}\n"
            f"💰 Ish haqi: {instance.salary}\n"
            f"📍 Lokatsiya: {instance.location}\n"
            f"🧾 Talablar: {instance.requirements}\n"
            f"📞 Aloqa: {instance.contact_info}"
        )
        try:
            bot.send_message(chat_id=CHANNEL_ID, text=text, parse_mode="Markdown")
        except Exception as e:
            print(f"Xatolik: {e}")
