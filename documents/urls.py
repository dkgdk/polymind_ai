# documents/urls.py
from django.urls import path
from .views import (
    SupportedModelsView,
    DocumentUploadView,
    DocumentListView,
    DocumentDetailView,
    ToggleFavouriteView,
    AskQuestionView,
    DocumentSummaryView,
    ChatSessionListView,
    ChatSessionDetailView,
    DashboardView,
)

urlpatterns = [
    path('models/',                  SupportedModelsView.as_view(),    name='doc-models'),
    path('dashboard/',               DashboardView.as_view(),          name='doc-dashboard'),
    path('upload/',                  DocumentUploadView.as_view(),     name='doc-upload'),
    path('ask/',                     AskQuestionView.as_view(),        name='general-ask'),
    path('chats/',                   ChatSessionListView.as_view(),    name='general-chats'),
    path('chats/<int:pk>/',          ChatSessionDetailView.as_view(),  name='general-chat-detail'),
    path('',                         DocumentListView.as_view(),       name='doc-list'),
    path('<int:pk>/',                DocumentDetailView.as_view(),     name='doc-detail'),
    path('<int:pk>/favourite/',      ToggleFavouriteView.as_view(),    name='doc-favourite'),
    path('<int:pk>/ask/',            AskQuestionView.as_view(),        name='doc-ask'),
    path('<int:pk>/summary/',        DocumentSummaryView.as_view(),    name='doc-summary'),
    path('<int:pk>/chats/',          ChatSessionListView.as_view(),    name='doc-chats'),
    path('<int:pk>/chats/<int:chat_id>/', ChatSessionDetailView.as_view(), name='doc-chat-detail'),
]
