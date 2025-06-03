from django.contrib import admin
from .models import Vacancy, User


@admin.register(Vacancy)
class VacancyAdmin(admin.ModelAdmin):
    list_display = ("title", "company_name")
    search_fields = ("title",)
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    pass