# submission/models.py

from django.db import models
from problems.models import Problem
from django.contrib.auth.models import User

class CodeSubmission(models.Model):
    LANGUAGES = [
        ('cpp', 'C++'),
        ('py', 'Python'),
        ('java', 'Java'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE, related_name='submissions')
    code = models.TextField()
    language = models.CharField(max_length=10, choices=LANGUAGES)
    submitted_at = models.DateTimeField(auto_now_add=True)
    verdict = models.CharField(max_length=20, blank=True, null=True)
    output = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.problem.problem_name} - {self.language} - {self.verdict}"
