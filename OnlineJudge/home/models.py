from django.db import models

class problem(models.Model):
    problem_name = models.CharField(max_length=100)
    problem_difficulty = models.IntegerField()
    statement = models.TextField(max_length=500)
    constraints = models.TextField(max_length=500)

    def __str__(self):
        return self.problem_name
