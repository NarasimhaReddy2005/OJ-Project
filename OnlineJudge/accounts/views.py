# views.py
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, PasswordChangeForm, PasswordResetForm, SetPasswordForm
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.conf import settings
from django.http import HttpResponse

# Register view
def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'auth/register.html', {'form': form})

# Login view
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('/')
    else:
        form = AuthenticationForm()
    return render(request, 'auth/login.html', {'form': form})

# Logout view
def logout_view(request):
    logout(request)
    return redirect('login')

# Profile view
# def profile_view(request):
#     if not request.user.is_authenticated:
#         return redirect('login')
#     return render(request, 'auth/profile.html')

# Password change view
def change_password_view(request):
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            return redirect('profile')
    else:
        form = PasswordChangeForm(user=request.user)
    return render(request, 'auth/change_password.html', {'form': form})

# Password reset request
def password_reset_request_view(request):
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            user_email = form.cleaned_data['email']
            user = User.objects.filter(email=user_email).first()
            if user:
                token = default_token_generator.make_token(user)
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                reset_url = request.build_absolute_uri(f'/password-reset-confirm/{uid}/{token}/')
                message = f'Click the link to reset your password: {reset_url}'
                send_mail('Reset your password', message, settings.DEFAULT_FROM_EMAIL, [user_email])
            return HttpResponse('Password reset link sent (if user exists).')
    else:
        form = PasswordResetForm()
    return render(request, 'auth/password_reset.html', {'form': form})

# Password reset confirm
def password_reset_confirm_view(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (User.DoesNotExist, ValueError):
        user = None

    if user and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            form = SetPasswordForm(user, request.POST)
            if form.is_valid():
                form.save()
                return redirect('login')
        else:
            form = SetPasswordForm(user)
        return render(request, 'auth/password_reset_confirm.html', {'form': form})
    else:
        return HttpResponse('Invalid reset link.')
