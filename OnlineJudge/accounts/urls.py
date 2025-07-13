# accounts/urls.py
from django.urls import path
from .views import login_view, logout_view, register_user

urlpatterns = [
    path('register/', register_user, name='register-user'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
]
