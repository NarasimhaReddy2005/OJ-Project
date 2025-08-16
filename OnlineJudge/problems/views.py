import json
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from problems.utils import get_latest_submissions
from django.core.serializers.json import DjangoJSONEncoder
from .models import Problem

@login_required
def problem_detail_view(request, problem_id):
    selected_problem = get_object_or_404(Problem, pk=problem_id)

    try:
        latest_submissions = get_latest_submissions(request.user, selected_problem)
    except Exception:
        latest_submissions = {}

    latest_lang = None
    latest_time = None

    for lang, sub in latest_submissions.items():
        if sub and (latest_time is None or sub["submitted_at"] > latest_time):
            latest_time = sub["submitted_at"]
            latest_lang = sub["language"] 

    latest_submissions_json = json.dumps(latest_submissions, cls=DjangoJSONEncoder)  # convert to JSON string

    return render(request, 'problems/problem_detail.html', {
        "problem": selected_problem,
        "latest_lang": latest_lang if latest_lang else "cpp",
        "latest_submissions_json": latest_submissions_json,  # clearer name
    })
