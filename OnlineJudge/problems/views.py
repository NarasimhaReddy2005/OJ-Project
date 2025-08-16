from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from submission.models import CodeSubmission
from .models import Problem
# Create your views here.

@login_required  # type: ignore
def problem_detail_view(request, problem_id):
    selected_problem = get_object_or_404(Problem, pk=problem_id)

    latest_submission = None
    try:
        latest_submission = CodeSubmission.objects.filter(
            user=request.user,
            problem=selected_problem
        ).latest('submitted_at')
    except CodeSubmission.DoesNotExist:
        pass  # no submissions yet

    return render(request, 'problems/problem_detail.html', {
        'problem': selected_problem,
        'latest_code': latest_submission.code if latest_submission else "",
        'latest_lang': latest_submission.language if latest_submission else "",
    })