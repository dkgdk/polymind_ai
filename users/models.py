# users/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    phone = models.CharField(
        max_length = 15,
        blank      = True,
        null       = True
    )
    bio = models.TextField(blank=True, null=True)

    # Multi-Model & Dedicated Provider API Keys
    mistral_api_key = models.CharField(max_length=255, blank=True, null=True)
    openai_api_key = models.CharField(max_length=255, blank=True, null=True)
    openrouter_api_key = models.CharField(max_length=255, blank=True, null=True)
    gemini_api_key = models.CharField(max_length=255, blank=True, null=True)
    groq_api_key = models.CharField(max_length=255, blank=True, null=True)

    preferred_model = models.CharField(
        max_length=100,
        default='mistralai/mistral-7b-instruct:free'
    )

    # Email login
    USERNAME_FIELD  = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email

    @property
    def documents_count(self):
        return self.documents.count()
