from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import CustomUser


# ── Register Serializer ───────────────
class RegisterSerializer(serializers.ModelSerializer):
    password  = serializers.CharField(
        write_only = True,
        validators = [validate_password]
    )
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model  = CustomUser
        fields = ['id', 'email', 'username', 'password', 'password2']

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError(
                {'password': 'Passwords match nahi karte!'}
            )
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        return CustomUser.objects.create_user(**validated_data)


# ── Profile & AI Settings Serializer ──
class ProfileSerializer(serializers.ModelSerializer):
    documents_count = serializers.ReadOnlyField()

    class Meta:
        model  = CustomUser
        fields = [
            'id', 'email', 'username',
            'first_name', 'last_name',
            'phone', 'bio',
            'mistral_api_key', 'openai_api_key', 'openrouter_api_key',
            'gemini_api_key', 'groq_api_key',
            'preferred_model',
            'documents_count',
            'date_joined'
        ]
        read_only_fields = ['email', 'date_joined']


# ── Change Password Serializer ────────
class ChangePasswordSerializer(serializers.Serializer):
    old_password  = serializers.CharField(write_only=True)
    new_password  = serializers.CharField(
        write_only = True,
        validators = [validate_password]
    )
    new_password2 = serializers.CharField(write_only=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password2']:
            raise serializers.ValidationError(
                {'new_password': 'Passwords match nahi karte!'}
            )
        return attrs
