# config/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from . import template_views

@api_view(['GET'])
@permission_classes([AllowAny])
def api_root(request):
    return Response({
        'status': 'online',
        'message': 'PolyMind AI REST API Backend',
        'frontend_views': {
            'chat': '/chat/',
            'settings': '/settings/',
            'profile': '/profile/',
            'auth': '/auth/',
        },
        'endpoints': {
            'users': {
                'register': '/api/users/register/',
                'login': '/api/users/login/',
                'refresh_token': '/api/users/token/refresh/',
                'profile': '/api/users/profile/',
                'change_password': '/api/users/change-password/',
                'logout': '/api/users/logout/',
            },
            'documents_and_ai': {
                'models': '/api/documents/models/',
                'documents_list': '/api/documents/',
                'upload_pdf': '/api/documents/upload/',
                'dashboard_stats': '/api/documents/dashboard/',
                'general_chat_ask': '/api/documents/ask/',
                'general_chat_sessions': '/api/documents/chats/',
                'document_detail': '/api/documents/<id>/',
                'document_ask': '/api/documents/<id>/ask/',
                'document_summary': '/api/documents/<id>/summary/',
                'document_chats': '/api/documents/<id>/chats/',
                'document_favourite': '/api/documents/<id>/favourite/',
            }
        }
    })

urlpatterns = [
    # Frontend HTML Views
    path('', template_views.chat_view, name='home'),
    path('chat/', template_views.chat_view, name='chat-view'),
    path('settings/', template_views.settings_view, name='settings-view'),
    path('profile/', template_views.profile_view, name='profile-view'),
    path('auth/', template_views.login_view, name='auth-view'),
    path('api-root/', api_root, name='api-root'),

    # Admin
    path('admin/', admin.site.urls),

    # REST APIs
    path('api/users/',     include('users.urls')),
    path('api/documents/', include('documents.urls')),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
