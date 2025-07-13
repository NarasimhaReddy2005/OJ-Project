from django.contrib.auth.models import User
from django.http import HttpResponse
from django.template import loader
from django.shortcuts import redirect
from django.contrib import messages


# Create your views here.
def register_user(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = User.objects.filter(username=username)

        if(user.exists()):
            messages.error(request, "Username already exists")
            return redirect("/auth/register/")

        user = User.objects.create_user(username=username, password=password)

        user.save()

        messages.info(request, "User created successfully")
        return redirect("/auth/login/")

    template = loader.get_template('register_user.html')
    context = {}
    return HttpResponse(template.render(context, request))


def login_view():
    return None


def logout_view():
    return None