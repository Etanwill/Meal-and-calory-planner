from django.db import models
from django.contrib.auth.models import User

class UserRecommendation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    dietary_preferences = models.CharField(max_length=100, blank=True)
    fitness_goal = models.CharField(max_length=100, blank=True)
    lifestyle_factor = models.CharField(max_length=100, blank=True)
    dietary_restrictions = models.CharField(max_length=100, blank=True)
    health_condition = models.CharField(max_length=100, blank=True)
    your_query = models.TextField(blank=True)

    def __str__(self):
        return f"Recommendation for {self.user}"
