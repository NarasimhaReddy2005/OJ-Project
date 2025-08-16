from django.shortcuts import render, get_object_or_404
from submission.models import CodeSubmission
from problems.models import Problem
from django.http import JsonResponse

def ai_review_modal(request, problem_id):
    try:
        submission = CodeSubmission.objects.filter(problem_id=problem_id).latest('submitted_at')
    except CodeSubmission.DoesNotExist:
        return JsonResponse({'error': 'No submissions done yet'}, status=404)

    context = {
        'problem_statement': submission.problem.statement,
        'language': submission.language,
        'verdict': submission.verdict,
        'code': submission.code,
        'submission_id': submission.id
    }
    return render(request, 'ai/popup.html', context)
