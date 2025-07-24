from django.db import models
from django.conf import settings
import os

# Create your models here.
class Problem(models.Model):
    DIFFICULTY_CHOICES = [
        (1, 'Easy'),
        (2, 'Medium'),
        (3, 'Hard'),
    ]
    # If your model define like this
    # Then Django automatically adds this method:
    # problem.get_problem_difficulty_display()
    # And in templates, you just do:
    # {{problem.get_problem_difficulty_display}}

    problem_name = models.CharField(max_length=100)
    problem_difficulty = models.IntegerField(choices=DIFFICULTY_CHOICES)
    statement = models.TextField(max_length=3000)
    constraints = models.TextField(max_length=500)

class TestCaseBundle(models.Model):
    problem = models.OneToOneField(Problem, on_delete=models.CASCADE, related_name='testcase_bundle')
    testcases_dir = models.CharField(max_length=255, help_text="Relative to MEDIA_ROOT/testcases/")

    def get_full_path(self):
        return os.path.join(settings.MEDIA_ROOT, 'testcases', self.testcases_dir)

    def __str__(self):
        return f"Test cases for {self.problem.problem_name}"
    
