from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Problem
# Create your views here.

@login_required # type: ignore
def problem_detail_view(request, problem_id):
    selected_problem = get_object_or_404(Problem, pk=problem_id)
    return render(request, 'problems/problem_detail.html', {
        'problem': selected_problem,
    })