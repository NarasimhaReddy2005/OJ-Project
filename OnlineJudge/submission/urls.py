from django.urls import path
from submission.views import run

urlpatterns = [
    path("run/", run, name="run"),
]