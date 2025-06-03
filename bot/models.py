from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    telegram_id = models.BigIntegerField(unique=True, null=True, blank=True)

# bot/models.py
class Vacancy(models.Model):
    company_name = models.CharField(max_length=255)
    title = models.CharField(max_length=255)
    salary = models.CharField(max_length=100)
    location = models.CharField(max_length=255)
    requirements = models.TextField()
    contact_info = models.CharField(max_length=255)
    telegram_username = models.CharField(max_length=255, null=True, blank=True, default='-')
    appeal_time = models.CharField(max_length=255)          # yangi
    responsible_person = models.CharField(max_length=255)   # yangi
    working_hours = models.CharField(max_length=255)        # yangi
    created_at = models.DateTimeField(auto_now_add=True)


