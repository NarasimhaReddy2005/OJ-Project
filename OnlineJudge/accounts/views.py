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
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from .models import UserMetadata
from submission.models import CodeSubmission
from problems.models import Problem
from django.db.models import Count
from django.utils.timezone import now
from datetime import timedelta
import calendar

# Register view
def register_view(request):
    if request.user.is_authenticated:
        return redirect('/')
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
    if request.user.is_authenticated:
        return redirect('/')

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
# def change_password_view(request):
#     if request.method == 'POST':
#         form = PasswordChangeForm(user=request.user, data=request.POST)
#         if form.is_valid():
#             user = form.save()
#             update_session_auth_hash(request, user)
#             return redirect('profile')
#     else:
#         form = PasswordChangeForm(user=request.user)
#     return render(request, 'auth/change_password.html', {'form': form})

# # Password reset request
# def password_reset_request_view(request):
#     if request.method == 'POST':
#         form = PasswordResetForm(request.POST)
#         if form.is_valid():
#             user_email = form.cleaned_data['email']
#             user = User.objects.filter(email=user_email).first()
#             if user:
#                 token = default_token_generator.make_token(user)
#                 uid = urlsafe_base64_encode(force_bytes(user.pk))
#                 reset_url = request.build_absolute_uri(f'/password-reset-confirm/{uid}/{token}/')
#                 message = f'Click the link to reset your password: {reset_url}'
#                 send_mail('Reset your password', message, settings.DEFAULT_FROM_EMAIL, [user_email])
#             return HttpResponse('Password reset link sent (if user exists).')
#     else:
#         form = PasswordResetForm()
#     return render(request, 'auth/password_reset.html', {'form': form})

# # Password reset confirm
# def password_reset_confirm_view(request, uidb64, token):
#     try:
#         uid = force_str(urlsafe_base64_decode(uidb64))
#         user = User.objects.get(pk=uid)
#     except (User.DoesNotExist, ValueError):
#         user = None

#     if user and default_token_generator.check_token(user, token):
#         if request.method == 'POST':
#             form = SetPasswordForm(user, request.POST)
#             if form.is_valid():
#                 form.save()
#                 return redirect('login')
#         else:
#             form = SetPasswordForm(user)
#         return render(request, 'auth/password_reset_confirm.html', {'form': form})
#     else:
#         return HttpResponse('Invalid reset link.')


@login_required
def user_profile(request):
    user = request.user
    metadata, created = UserMetadata.objects.get_or_create(user=user)

    # Submissions grouped by day (last 7 days)
    today = now().date()
    past_week = [today - timedelta(days=i) for i in range(6, -1, -1)]
    daily_submissions = (
        CodeSubmission.objects.filter(user=user, submitted_at__date__in=past_week)
        .extra(select={'day': "DATE(submitted_at)"})
        .values('day')
        .annotate(count=Count('id'))
    )

    # Prepare chart data
    submission_dict = {str(day): 0 for day in past_week}
    for entry in daily_submissions:
        submission_dict[str(entry['day'])] = entry['count']

    activity_labels = [day.strftime('%a') for day in past_week]  # ['Mon', 'Tue', ...]
    activity_counts = list(submission_dict.values())             # [3, 5, 0, ...]

    # Problems solved
    solved_problems = (
        CodeSubmission.objects.filter(user=user, verdict="Accepted")
        .values('problem')
        .distinct()
        .count()
    )
    total_problems = Problem.objects.count()
    solved_percent = round((solved_problems / total_problems) * 100, 1) if total_problems else 0

    context = {
        'user': user,
        'metadata': metadata,
        'activity_labels': activity_labels,
        'activity_counts': activity_counts,
        'solved_count': solved_problems,
        'solved_percent': solved_percent,
        'total_problems': total_problems,
    }

    return render(request, 'auth/profile_view.html', context)

from .models import UserMetadata
from .forms import UserMetadataForm
from django.views.decorators.http import require_GET, require_POST

def _get_or_create_metadata(user):
    # Ensure the user always has a metadata row
    metadata, _ = UserMetadata.objects.get_or_create(user=user)
    return metadata

@login_required
@require_GET
def metadata_get(request):
    metadata = _get_or_create_metadata(request.user)
    data = {
        'username': request.user.username,
        'bio': metadata.bio or '',
        'email': metadata.email or '',
        'linkedin': metadata.linkedin or '',
        'profile_picture_url': metadata.profile_picture.url if metadata.profile_picture else '',
        'date_joined': request.user.date_joined.strftime('%B %d, %Y'),
    }
    return JsonResponse({'ok': True, 'data': data})

@login_required
@require_POST
def metadata_update(request):
    metadata = _get_or_create_metadata(request.user)
    form = UserMetadataForm(request.POST, request.FILES, instance=metadata)
    if form.is_valid():
        md = form.save()

        # Build the minimal payload needed to update the visible card
        payload = {
            'bio': md.bio or '',
            'email': md.email or '',
            'linkedin': md.linkedin or '',
            'profile_picture_url': md.profile_picture.url if md.profile_picture else '',
        }
        return JsonResponse({'ok': True, 'data': payload})
    else:
        # Return field errors
        return JsonResponse({'ok': False, 'errors': form.errors}, status=400)
        