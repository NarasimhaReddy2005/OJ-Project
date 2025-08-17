from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    # path('change-password/', views.change_password_view, name='change_password'),
    # path('password-reset/', views.password_reset_request_view, name='password_reset'),
    # path('password-reset-confirm/<uidb64>/<token>/', views.password_reset_confirm_view, name='password_reset_confirm'),
    path('profile/', views.user_profile, name='profile'),
    path('profile/metadata/', views.metadata_get, name='metadata_get'),       # GET current values (JSON)
    path('profile/metadata/update/', views.metadata_update, name='metadata_update'),  # POST updates
]
