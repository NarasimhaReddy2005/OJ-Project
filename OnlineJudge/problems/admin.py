from django.contrib import admin
from .models import Problem, TestCaseBundle  # or Problem if you used PascalCase

class TestCaseBundleInline(admin.StackedInline):
    model = TestCaseBundle
    extra = 0

@admin.register(Problem)
class ProblemAdmin(admin.ModelAdmin):
    list_display = ['problem_name', 'problem_difficulty']
    inlines = [TestCaseBundleInline]