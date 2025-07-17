from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.template import loader
from django.shortcuts import render
from django.core.paginator import Paginator
from .models import problem


# Create your views here.
def home(request):
    return render(request, 'home/home.html')

@login_required
def problem_detail(request, problem_id):
    req_problem = problem.objects.get(id=problem_id)

    context = {
        'problem': req_problem
    }
    template = loader.get_template('home/problem.html')
    return HttpResponse(template.render(context, request));


# Dummy data for now
dummy_problems = [
    {'title': f'Problem {i}', 'difficulty': 'Easy' if i % 3 == 0 else 'Medium' if i % 3 == 1 else 'Hard'}
    for i in range(1, 101)  # 100 dummy problems
]

def problems_list_view(request):
    page_number = request.GET.get('page', 1)
    paginator = Paginator(dummy_problems, 20)
    page_obj = paginator.get_page(page_number)

    template = loader.get_template('home/problems_list.html')
    context = {
        'problems': page_obj.object_list,
        'page_obj': page_obj
    }
    return HttpResponse(template.render(context, request))


