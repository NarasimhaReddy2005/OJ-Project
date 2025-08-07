from django.shortcuts import render
import os
import json
import google.generativeai as genai
from django.views.decorators.csrf import csrf_exempt
from dotenv import load_dotenv
from django.http import JsonResponse
from submission.models import CodeSubmission

# Create your views here.

def ai_review(request, submission_id):
    try:
        submission = CodeSubmission.objects.select_related('problem').get(id=submission_id)

        return JsonResponse({
            "problem_statement": submission.problem.statement,
            "code": submission.code,
            "verdict": submission.verdict,
            "language": submission.language,
        })

    except CodeSubmission.DoesNotExist:
        return JsonResponse({"error": "Submission not found"}, status=404)

load_dotenv()

genai.configure(api_key=os.getenv("GOOGLE_GEMINI_API    "))

@csrf_exempt
def generate_ai_review(request):
    if request.method != "POST":
        return JsonResponse({"error": "Only POST allowed"}, status=405)

    try:
        data = json.loads(request.body)
        problem = data.get("problem_statement", "")
        code = data.get("code", "")
        verdict = data.get("verdict", "")
        language = data.get("language", "cpp")

        if not code or not problem:
            return JsonResponse({"error": "Missing code or problem statement"}, status=400)

        # ✅ Dummy static review for frontend testing
        dummy_review = f"""
AI Review Summary:

🟢 **Correct Parts**:
- The code compiles and prints something.
- Syntax appears correct for C++.

🔴 **Issues Found**:
- The output is hardcoded as "Hello world!".
- You are not reading input or computing the required result based on the problem statement.

💡 **Suggestions**:
- Parse the input values as per constraints.
- Apply the algorithm logic to solve the problem.
- Match output format exactly, including case sensitivity.

Verdict: ❌ Likely Wrong Answer
        """

        return JsonResponse({"ai_response": dummy_review})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
