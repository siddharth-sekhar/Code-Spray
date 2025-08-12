"""
URL configuration for OnlineJudgeProject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', other_app.views.Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from django.http import HttpResponse
from users import views as user_views

def health_check(request):
    return HttpResponse("OK", status=200)

def root_view(request):
    return HttpResponse("Online Judge Project is running!", status=200)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('users/', include('users.urls')),               # Login, Dashboard
    path('problems/', include('problems.urls')),         # Problem list & detail
    
    # Direct access to login and dashboard for convenience
    path('login/', user_views.user_login, name='login_root'),
    path('dashboard/', user_views.dashboard, name='dashboard_root'),

    path('health/', health_check, name='health_check'),  # Health check endpoint
    path('', root_view, name='root'),  # Simple root view for debugging
]
