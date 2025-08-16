from submission.models import CodeSubmission

def get_latest_submissions(user, problem):
    languages = ["cpp", "python", "java"]
    latest_data = {}

    for lang in languages:
        sub = (
            CodeSubmission.objects.filter(user=user, problem=problem, language=lang)
            .order_by("-submitted_at")
            .first()
        )
        if sub:
            latest_data[lang] = {
                "id": sub.id,
                "verdict": sub.verdict,
                "code": sub.code,
                "language": sub.language,
                "submitted_at": sub.submitted_at,
            }
        else:
            latest_data[lang] = None

    return latest_data
