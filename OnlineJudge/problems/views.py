from django.shortcuts import render, get_object_or_404
from .models import Problem
# Create your views here.

def problem_detail_view(request, problem_id):
    selected_problem = get_object_or_404(Problem, pk=problem_id)
    return render(request, 'problems/problem_detail.html', {
        'problem': selected_problem
    })