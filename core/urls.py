"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, reverse_lazy
from django.views.generic.base import RedirectView
from dotenv import load_dotenv
import os

load_dotenv()


def root_redirect(request):
    if request.user.is_authenticated:
        return redirect('home')  # Redirect to home if logged in
    return redirect('signin')  # Redirect to signin if not logged in

urlpatterns = [
    path(os.getenv('ADMIN_URL'), admin.site.urls),
    path('', RedirectView.as_view(url=reverse_lazy('home'), permanent=True), name='root_redirect'),
    path("accounts/", include("allauth.urls")),
    path('users/', include('users.urls')),
    path('task/', include('tasks.urls')),
    path('api/', include('api.urls')),
    path('routine/', include('routines.urls')),
]