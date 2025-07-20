from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.template import loader
from django.shortcuts import render
from django.core.paginator import Paginator
from problems.models import Problem


# Create your views here.
def home(request):
    return render(request, 'home/home.html')

@login_required
def problem_detail(request, problem_id):
    req_problem = Problem.objects.get(id=problem_id)

    context = {
        'problem': req_problem
    }
    template = loader.get_template('home/problem.html')
    return HttpResponse(template.render(context, request))

def problems_list_view(request):
    query = request.GET.get('q')
    all_problems = Problem.objects.all()

    if query:
        all_problems = all_problems.filter(problem_name__icontains=query)

    paginator = Paginator(all_problems, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    template = loader.get_template('home/problems_list.html')
    context = {
        'problems': page_obj.object_list,
        'page_obj': page_obj
    }
    return HttpResponse(template.render(context, request))


