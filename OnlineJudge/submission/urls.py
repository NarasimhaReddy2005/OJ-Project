from django.urls import path
from problems import views
from submission.views import run, submit_code, user_activity

urlpatterns = [
    path("run/", run, name="run"),
    path("submit/<int:problem_id>/", submit_code, name="submit_code"),
    path('activity/', user_activity, name='user_activity'),]