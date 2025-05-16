from django.db import models

class UserRecommendation(models.Model):
    dietary_preferences = models.CharField(max_length=255)
    fitness_goal = models.CharField(max_length=255)
    lifestyle_factor = models.CharField(max_length=255)
    dietary_restrictions = models.CharField(max_length=255, blank=True)
    health_condition = models.CharField(max_length=255, blank=True)
    your_query = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.dietary_preferences} - {self.fitness_goal}"
