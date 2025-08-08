from django.db import models
from django.contrib.auth.models import User

LANG_CHOICES = [
    ('c', 'C'),
    ('cpp', 'C++'),
    ('java', 'Java'),
    ('python', 'Python'),
]

class Topic(models.Model):
    name = models.CharField(max_length=100)
    def __str__(self):
        return self.name

class Problem(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    input_desc = models.TextField(blank=True)
    output_desc = models.TextField(blank=True)
    constraints = models.TextField(blank=True)

    def __str__(self):
        return self.title

class TestCase(models.Model):
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
    input_data = models.TextField()
    output_data = models.TextField()

    def __str__(self):
        return f"TestCase for {self.problem.title}"

class Submission(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
    language = models.CharField(choices=LANG_CHOICES, max_length=10)
    code = models.TextField()
    status = models.CharField(max_length=15, default='Pending')  # AC, WA, TLE, RE, Pending
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} submission on {self.problem.title} [{self.status}]"
