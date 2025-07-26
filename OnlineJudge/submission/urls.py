from django.urls import path
from submission.views import run, submit_code

urlpatterns = [
    path("run/", run, name="run"),
    path("submit/<int:problem_id>/", submit_code, name="submit_code"),
]