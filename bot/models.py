from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    telegram_id = models.BigIntegerField(unique=True, null=True, blank=True)

class Vacancy(models.Model):
    company_name = models.CharField(max_length=255)
    title = models.CharField(max_length=255)
    salary = models.CharField(max_length=100)
    location = models.CharField(max_length=255)
    requirements = models.TextField()
    contact_info = models.TextField()
    is_confirmed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

class TelegramGroup(models.Model):
    name = models.CharField(max_length=255)
    group_id = models.CharField(max_length=100)  # -10012345678

class TelegramChannel(models.Model):
    name = models.CharField(max_length=255)
    channel_id = models.CharField(max_length=100)  # -100...

class VacancyDistribution(models.Model):
    vacancy = models.ForeignKey(Vacancy, on_delete=models.CASCADE)
    group = models.ForeignKey(TelegramGroup, on_delete=models.SET_NULL, null=True, blank=True)
    channel = models.ForeignKey(TelegramChannel, on_delete=models.SET_NULL, null=True, blank=True)
    sent_at = models.DateTimeField(auto_now_add=True)
