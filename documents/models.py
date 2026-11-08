# documents/models.py
from django.db import models
from django.conf import settings


class Document(models.Model):

    STATUS_CHOICES = [
        ('processing', 'Processing'),
        ('ready',      'Ready'),
        ('failed',     'Failed'),
    ]

    user         = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete    = models.CASCADE,
        related_name = 'documents'
    )
    title        = models.CharField(max_length=255)
    file         = models.FileField(upload_to='documents/')
    file_size    = models.PositiveIntegerField(default=0)
    pages        = models.PositiveIntegerField(default=0)
    status       = models.CharField(
        max_length = 20,
        choices    = STATUS_CHOICES,
        default    = 'processing'
    )
    summary      = models.TextField(blank=True, null=True)
    key_points   = models.JSONField(default=list, blank=True)
    is_favourite = models.BooleanField(default=False)
    tags         = models.JSONField(default=list, blank=True)
    created_at   = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} — {self.user.email}"

    @property
    def file_size_mb(self):
        return round(self.file_size / (1024 * 1024), 2)

    @property
    def chat_count(self):
        return self.chats.count()

    class Meta:
        ordering = ['-created_at']


class ChatSession(models.Model):
    # Nullable document so users can have pure general chat without documents
    document   = models.ForeignKey(
        Document,
        on_delete    = models.CASCADE,
        related_name = 'chats',
        null         = True,
        blank        = True
    )
    user       = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete    = models.CASCADE,
        related_name = 'general_chats',
        null         = True,
        blank        = True
    )
    title      = models.CharField(max_length=255, default='New Chat')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        doc_title = self.document.title if self.document else "General Chat"
        return f"{doc_title} — {self.title}"

    @property
    def message_count(self):
        return self.messages.count()

    class Meta:
        ordering = ['-updated_at']


class ChatMessage(models.Model):
    ROLE_CHOICES = [
        ('user',      'User'),
        ('assistant', 'Assistant'),
    ]

    session    = models.ForeignKey(
        ChatSession,
        on_delete    = models.CASCADE,
        related_name = 'messages'
    )
    role       = models.CharField(max_length=20, choices=ROLE_CHOICES)
    content    = models.TextField()
    image      = models.TextField(blank=True, null=True)  # Base64 data URL or image URL
    sources    = models.JSONField(default=list, blank=True)
    model_name = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.role}: {self.content[:50]}"

    class Meta:
        ordering = ['created_at']
