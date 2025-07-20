from django.contrib import admin
from .models import Problem  # or Problem if you used PascalCase

@admin.register(Problem)
class ProblemAdmin(admin.ModelAdmin):
    list_display = ('id', 'problem_name', 'problem_difficulty')
