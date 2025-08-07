# ai/utils.py

REVIEW_PROMPT_TEMPLATE = """
You are an AI code reviewer. Given the following problem statement, verdict,
and user-submitted code, provide constructive feedback to help the user improve:

🧠 Problem Statement:
{problem}

📥 Verdict:
{verdict}

📄 Code (language: {language}):
```{language}
{code}
```

Respond in clear and concise bullet points using these markers:

✅ - For what is done well
⚠️ - For potential issues
📌 - For suggestions or improvements

Focus on logic, structure, style, and readability. Keep the tone supportive and informative.
"""
