from django.contrib import admin
from .models import Vacancy, TelegramGroup, TelegramChannel, VacancyDistribution, User


@admin.register(Vacancy)
class VacancyAdmin(admin.ModelAdmin):
    list_display = ("title", "company_name", "is_confirmed")
    search_fields = ("title",)
    list_filter = ("is_confirmed",)
admin.site.register(TelegramGroup)
admin.site.register(TelegramChannel)
admin.site.register(VacancyDistribution)
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    pass