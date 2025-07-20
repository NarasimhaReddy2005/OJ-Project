# home\urls.py

from django.urls import path

from . import views
from .views import home

urlpatterns = [
    path('', home, name='home'),
    path('problems_list/', views.problems_list_view, name='problems'),
]