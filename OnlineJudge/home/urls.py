# home\urls.py

from django.urls import path

from . import views
from .views import home

urlpatterns = [
    path('', home, name='home'),
    path('problems/', views.problems_list_view, name='problems'),
]