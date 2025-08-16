from django.shortcuts import render, get_object_or_404
import os
import json
import google.generativeai as genai
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from dotenv import load_dotenv
from django.http import HttpResponseForbidden, JsonResponse
from submission.models import CodeSubmission
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from submission.models import CodeSubmission
from ai.utils import REVIEW_PROMPT_TEMPLATE
import markdown

# Create your views here.

def ai_review(request, submission_id):
    submission = get_object_or_404(CodeSubmission.objects.select_related('problem'), id=submission_id)

    context = {
        "problem_statement": submission.problem.statement,
        "code": submission.code,
        "verdict": submission.verdict,
        "language": submission.language,
        "submission_id": submission.id,
    }

    return render(request, 'ai/ai_review.html', context)

# Set API key (ideally from environment)
load_dotenv()
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

@login_required
def ai_generate_review(request, submission_id):
    try:
        submission = CodeSubmission.objects.get(id=submission_id)
    except CodeSubmission.DoesNotExist:
        # Return JSON so frontend can show toast
        return JsonResponse({
            "success": False,
            "message": "No submission found here (ai's view)"
        })

    # Only allow AI review for specific verdicts
    if submission.verdict not in ["Wrong Answer", "Accepted"]:
        return HttpResponse("⚠️ AI Review only allowed for Wrong Answer or Accepted submissions.")

    # Format the prompt for Gemini
    prompt = REVIEW_PROMPT_TEMPLATE.format(
        problem=submission.problem.statement,
        verdict=submission.verdict,
        language=submission.language,
        code=submission.code,
    )

    try:
        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content(prompt)

        if hasattr(response, "text"):
            markdown_html = markdown.markdown(response.text, extensions=["fenced_code"])
            return HttpResponse(markdown_html)
        else:
            return HttpResponse("❌ Failed to get a valid response from Gemini.")

    except Exception as e:
        return HttpResponse(f"❌ Gemini API Error: {str(e)}", status=500)


# load_dotenv()

# genai.configure(api_key=os.getenv("GOOGLE_GEMINI_API    "))

# @csrf_exempt
# def generate_ai_review(request):
#     if request.method != "POST":
#         return JsonResponse({"error": "Only POST allowed"}, status=405)

#     try:
#         data = json.loads(request.body)
#         problem = data.get("problem_statement", "")
#         code = data.get("code", "")
#         verdict = data.get("verdict", "")
#         language = data.get("language", "cpp")

#         if not code or not problem:
#             return JsonResponse({"error": "Missing code or problem statement"}, status=400)

#         # ✅ Dummy static review for frontend testing
#         dummy_review = f"""
# AI Review Summary:

# 🟢 **Correct Parts**:
# - The code compiles and prints something.
# - Syntax appears correct for C++.

# 🔴 **Issues Found**:
# - The output is hardcoded as "Hello world!".
# - You are not reading input or computing the required result based on the problem statement.

# 💡 **Suggestions**:
# - Parse the input values as per constraints.
# - Apply the algorithm logic to solve the problem.
# - Match output format exactly, including case sensitivity.

# Verdict: ❌ Likely Wrong Answer
#         """

#         return JsonResponse({"ai_response": dummy_review})

#     except Exception as e:
#         return JsonResponse({"error": str(e)}, status=500)
