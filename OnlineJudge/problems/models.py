from django.db import models



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

    def __str__(self):
        return self.problem_name