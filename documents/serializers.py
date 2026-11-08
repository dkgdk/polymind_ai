# documents/serializers.py
from rest_framework import serializers
from .models import Document, ChatSession, ChatMessage


# ── Chat Message Serializer ───────────
class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model  = ChatMessage
        fields = ['id', 'role', 'content', 'image', 'sources', 'model_name', 'created_at']
        read_only_fields = ['id', 'created_at']


# ── Chat Session Serializer ───────────
class ChatSessionSerializer(serializers.ModelSerializer):
    messages      = ChatMessageSerializer(many=True, read_only=True)
    message_count = serializers.ReadOnlyField()

    class Meta:
        model  = ChatSession
        fields = [
            'id', 'title', 'document', 'message_count',
            'messages', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


# ── Document List Serializer ──────────
class DocumentListSerializer(serializers.ModelSerializer):
    file_size_mb = serializers.ReadOnlyField()
    chat_count   = serializers.ReadOnlyField()

    class Meta:
        model  = Document
        fields = [
            'id', 'title', 'status',
            'pages', 'file_size_mb',
            'is_favourite', 'tags',
            'chat_count', 'created_at'
        ]
        read_only_fields = ['id', 'status', 'pages', 'created_at']


# ── Document Detail Serializer ────────
class DocumentDetailSerializer(serializers.ModelSerializer):
    file_size_mb = serializers.ReadOnlyField()
    chat_count   = serializers.ReadOnlyField()
    chats        = ChatSessionSerializer(many=True, read_only=True)

    class Meta:
        model  = Document
        fields = [
            'id', 'title', 'file', 'status',
            'pages', 'file_size_mb',
            'summary', 'key_points',
            'is_favourite', 'tags',
            'chat_count', 'chats',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'status', 'pages',
            'summary', 'key_points',
            'created_at', 'updated_at'
        ]


# ── Upload Serializer ─────────────────
class DocumentUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Document
        fields = ['id', 'title', 'file', 'tags']

    def validate_file(self, value):
        if not value.name.lower().endswith('.pdf'):
            raise serializers.ValidationError("Sirf PDF files allowed hain!")
        if value.size > 10 * 1024 * 1024:
            raise serializers.ValidationError("File 10MB se chhoti honi chahiye!")
        return value


# ── Ask Question Serializer ───────────
class AskQuestionSerializer(serializers.Serializer):
    question    = serializers.CharField(max_length=4000, required=False, allow_blank=True, default='')
    image       = serializers.CharField(required=False, allow_blank=True, default='')
    session_id  = serializers.IntegerField(required=False)
    document_id = serializers.IntegerField(required=False, allow_null=True)
    model       = serializers.CharField(required=False, allow_blank=True)


# ── Chat Session Create Serializer ────
class ChatSessionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model  = ChatSession
        fields = ['id', 'title']
