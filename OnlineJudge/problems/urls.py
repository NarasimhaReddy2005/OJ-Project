# home\urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('<int:problem_id>/', views.problem_detail_view, name='problem_detail'),
]