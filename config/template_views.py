from django.shortcuts import render

def chat_view(request):
    """Main Chat Dashboard (Clean view, pure chat or doc QA, model switcher, history)"""
    return render(request, 'pages/chat.html')

def settings_view(request):
    """API Keys and Model Configuration Settings"""
    return render(request, 'pages/settings.html')

def profile_view(request):
    """User Profile and Account Info"""
    return render(request, 'pages/profile.html')

def login_view(request):
    """Login and Register Page"""
    return render(request, 'pages/auth.html')

