# users/views.py
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from .models import CustomUser
from .serializers import (
    RegisterSerializer,
    ProfileSerializer,
    ChangePasswordSerializer
)


# ── Register ──────────────────────────
class RegisterView(generics.CreateAPIView):
    """
    POST /api/users/register/
    Naya user banao
    """
    queryset           = CustomUser.objects.all()
    serializer_class   = RegisterSerializer
    permission_classes = [AllowAny]


# ── Profile ───────────────────────────
class ProfileView(APIView):
    """
    GET  /api/users/profile/ → Profile dekho
    PATCH /api/users/profile/ → Profile update karo
    DELETE /api/users/profile/ → Account delete karo
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = ProfileSerializer(request.user)
        return Response(serializer.data)

    def patch(self, request):
        serializer = ProfileSerializer(
            request.user,
            data    = request.data,
            partial = True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(
            serializer.errors,
            status = status.HTTP_400_BAD_REQUEST
        )

    def delete(self, request):
        request.user.delete()
        return Response(
            {'message': 'Account delete ho gaya!'},
            status = status.HTTP_204_NO_CONTENT
        )


# ── Change Password ───────────────────
class ChangePasswordView(APIView):
    """
    POST /api/users/change-password/
    Password change karo
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status = status.HTTP_400_BAD_REQUEST
            )

        # Old password check karo
        if not request.user.check_password(
            serializer.validated_data['old_password']
        ):
            return Response(
                {'error': 'Old password galat hai!'},
                status = status.HTTP_400_BAD_REQUEST
            )

        # New password set karo
        request.user.set_password(
            serializer.validated_data['new_password']
        )
        request.user.save()

        return Response({'message': 'Password change ho gaya!'})


# ── Logout ────────────────────────────
class LogoutView(APIView):
    """
    POST /api/users/logout/
    Refresh token blacklist karo
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            token = RefreshToken(request.data.get('refresh'))
            token.blacklist()
            return Response({'message': 'Logout successful!'})
        except Exception:
            return Response(
                {'error': 'Invalid token!'},
                status = status.HTTP_400_BAD_REQUEST
            )