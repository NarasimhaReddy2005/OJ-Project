from django.db import models
from django.conf import settings
import os
from django.utils.text import slugify

# Create your models here.
class Problem(models.Model):
    DIFFICULTY_CHOICES = [
        (1, 'Easy'),
        (2, 'Medium'),
        (3, 'Hard'),
    ]

    problem_name = models.CharField(max_length=100)
    problem_difficulty = models.IntegerField(choices=DIFFICULTY_CHOICES)
    statement = models.TextField(max_length=3000)
    constraints = models.TextField(max_length=500)

class TestCaseBundle(models.Model):
    problem = models.OneToOneField(Problem, on_delete=models.CASCADE, related_name='testcase_bundle')
    testcases_dir = models.CharField(max_length=255, blank=True, help_text="Relative to MEDIA_ROOT/testcases/")
    zip_file = models.FileField(upload_to='testcase_zips/', null=True, blank=True)

    def save(self, *args, **kwargs):
        # Auto-generate testcases_dir if not set
        if not self.testcases_dir:
            self.testcases_dir = f'problem_{self.problem.id or "new"}'

        # Rename the uploaded zip file based on problem
        if self.zip_file and hasattr(self.zip_file, 'name'):
            base, ext = os.path.splitext(self.zip_file.name)
            slug = slugify(self.problem.problem_name)
            new_name = f"{slug}_{self.problem.id or 'new'}{ext}"
            self.zip_file.name = f"testcase_zips/{new_name}"

        super().save(*args, **kwargs)

    def get_full_path(self):
        from django.conf import settings
        return os.path.join(settings.MEDIA_ROOT, 'testcases', self.testcases_dir)

    def __str__(self):
        return f"Test cases for {self.problem.problem_name}"
    
