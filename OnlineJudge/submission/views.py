import os
import subprocess
import tempfile
import json
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from problems.models import Problem, TestCaseBundle
from submission.models import CodeSubmission
from submission.utils import execute_code, run_code_and_check
from django.contrib.auth.decorators import login_required
from datetime import timedelta
from django.utils import timezone
from django.core.paginator import Paginator

@csrf_exempt
def run(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=400)

    try:
        data = json.loads(request.body)
        code = data.get('code', '')
        user_input = data.get('input', '')
        language = data.get('language', 'cpp')

        status, result = execute_code(code, language, user_input)

        if status == 'success':
            return JsonResponse({'output': result})
        elif status == 'timeout': 
            return JsonResponse({'error': result}) 
        elif status == 'compile_error': 
            return JsonResponse({'error': result}) 
        else: 
            return JsonResponse({'error': result})


    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_protect
def submit_code(request, problem_id):
    if request.method == 'POST':
        problem = get_object_or_404(Problem, id=problem_id)
        code = request.POST.get('code')
        language = request.POST.get('language')
        # Save the submission
        submission = CodeSubmission.objects.create(
            user=request.user,
            problem=problem,
            code=code,
            language=language
        )
        testcase_bundle = TestCaseBundle.objects.get(problem=problem)
        # Run and test
        verdict, output = run_code_and_check(code, language, testcase_bundle.get_full_path())

        # Save results
        submission.verdict = verdict
        submission.output = output
        submission.save()

        return JsonResponse({
            'verdict': verdict,
            'output': output
        })

    return JsonResponse({'error': 'Only POST allowed'}, status=405)

@login_required
def user_activity(request):
    # Get filter param from query string
    filter_days = request.GET.get('filter', '3')
    try:
        days = int(filter_days)
        if days > 0:
            date_limit = timezone.now() - timedelta(days=days)
            submissions = CodeSubmission.objects.filter(
                user=request.user,
                submitted_at__gte=date_limit
            )
        else:
            submissions = CodeSubmission.objects.filter(user=request.user)
    except ValueError:
        # fallback to default 3 days if invalid value
        submissions = CodeSubmission.objects.filter(user=request.user)

    submissions = submissions.order_by('-submitted_at')

    # Pagination
    paginator = Paginator(submissions, 20)  # 20 per page
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, 'submission/user_activity.html', {
        'page_obj': page_obj,
        'filter_days': filter_days,
    })

@login_required
def latest_submission(request, problem_id, language=None):
    try:
        problem = Problem.objects.get(id=problem_id)

        qs = CodeSubmission.objects.filter(user=request.user, problem=problem)
        if language:  # filter by language if provided
            qs = qs.filter(language=language)

        latest = qs.latest('submitted_at')

        return JsonResponse({
            'id': latest.id,
            'verdict': latest.verdict,
            'code': latest.code,
            'language': latest.language
        })
    except CodeSubmission.DoesNotExist:
        return JsonResponse({
            'error': 'No submissions found for this problem.'
        }, status=404)

