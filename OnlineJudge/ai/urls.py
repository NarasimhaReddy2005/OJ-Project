from django.urls import path
from . import views

urlpatterns = [
    path('review/<int:submission_id>/', views.ai_review, name='ai_review'),
    path("review/generate/", views.generate_ai_review, name="generate_ai_review")
]
