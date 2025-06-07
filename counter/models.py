from django.db import models
from django import forms
from django.contrib.auth.models import AbstractUser, Group, Permission

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

class FoodQueryForm(forms.Form):
    food_name = forms.CharField(label="Enter a Cameroonian food", max_length=100)

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=100)

    groups = models.ManyToManyField(
        Group,
        related_name='customuser_set',  # nom unique pour éviter conflit
        blank=True,
        help_text=(
            'The groups this user belongs to. A user will get all permissions '
            'granted to each of their groups.'
        ),
        related_query_name='customuser',
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='customuser_set',  # nom unique pour éviter conflit
        blank=True,
        help_text='Specific permissions for this user.',
        related_query_name='customuser',
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']  # ou ['full_name', 'username'] si tu préfères

    def __str__(self):
        return self.email
