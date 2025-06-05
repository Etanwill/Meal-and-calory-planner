from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views import View
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User

from rest_framework import viewsets
from .serializers import UserSerializer

from .models import UserRecommendation
from .recommendation_profiles import PERSONALIZED_RECOMMENDATIONS

import requests
import subprocess
from django.conf import settings


# Déconnexion
def logout_view(request):
    logout(request)
    return redirect('login')


# API REST des utilisateurs

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer



# Connexion
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'login.html')


# Inscription
def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
        else:
            user = User.objects.create_user(username=username, email=email, password=password)
            user.save()
            messages.success(request, 'Account created successfully. You can log in now.')
            return redirect('login')
    return render(request, 'register.html')


# Page d’accueil sécurisée
def home(request):
    if not request.user.is_authenticated:
        return redirect('login')

    api = None
    total = 0
    if request.method == "POST":
        query = request.POST.get('query')
        url = "https://trackapi.nutritionix.com/v2/natural/nutrients"
        headers = {
            "x-app-id": settings.NUTRITIONIX_APP_ID,
            "x-app-key": settings.NUTRITIONIX_APP_KEY,
            "Content-Type": "application/json"
        }
        data = {
            "query": query,
            "timezone": "US/Eastern"
        }

        try:
            response = requests.post(url, json=data, headers=headers)
            if response.status_code == 200:
                data = response.json()
                if "foods" in data:
                    api = [data["foods"][0]]
                    total = api[0].get("nf_calories", 0)
                else:
                    api = "Oops! There was an error with the response data."
            else:
                api = f"Oops! There was an error. Status code: {response.status_code}"
        except Exception as e:
            api = f"An error occurred: {str(e)}"

    return render(request, "home.html", {"api": api, "total": total})


# Générateur de recommandations personnalisées
def generate_manual_recommendation(data):
    best_score = 0
    best_match = None

    for profile in PERSONALIZED_RECOMMENDATIONS:
        score = 0
        conditions = profile.get("conditions", {})

        for key, value in conditions.items():
            if key in data:
                if value.lower() == data[key].lower():
                    score += 2
                elif value.lower() in data[key].lower() or data[key].lower() in value.lower():
                    score += 1

        if score > best_score:
            best_score = score
            best_match = profile

    if best_match:
        return {
            "diet_types": best_match.get("diet_types", []),
            "workouts": best_match.get("workouts", []),
            "breakfasts": best_match.get("breakfasts", []),
            "dinners": best_match.get("dinners", []),
            "additional_tips": best_match.get("additional_tips", [])
        }

    return {
        "diet_types": ["Balanced diet", "Whole food based", "Low sugar", "Low sodium", "Anti-inflammatory"],
        "workouts": ["Walking", "Yoga", "Light strength", "Pilates", "Stretching"],
        "breakfasts": ["Oatmeal with fruits", "Greek yogurt", "Eggs and toast", "Smoothie bowl", "Protein pancakes"],
        "dinners": ["Grilled chicken and veggies", "Salmon with quinoa", "Lentil soup", "Zucchini noodles", "Tofu stir fry"],
        "additional_tips": ["Drink 2L water/day", "Avoid processed foods", "Include healthy snacks", "Use natural supplements", "Sleep 7-8 hours"]
    }


# Vue des recommandations
def recommendation(request):
    if request.method == 'POST':
        data = {
            'dietary_preferences': request.POST.get('dietary_preferences', ''),
            'fitness_goal': request.POST.get('fitness_goal', ''),
            'lifestyle_factor': request.POST.get('lifestyle_factor', ''),
            'dietary_restrictions': request.POST.get('dietary_restrictions', ''),
            'health_condition': request.POST.get('health_condition', ''),
            'your_query': request.POST.get('your_query', ''),
        }

        if request.user.is_authenticated:
            UserRecommendation.objects.create(user=request.user, **data)
        else:
            UserRecommendation.objects.create(**data)

        recommendations = generate_manual_recommendation(data)
        return render(request, 'recommendation.html', {'recommendations': recommendations})

    return render(request, 'recommendation.html', {'recommendations': None})


# Vue pour lancer Streamlit dans un processus séparé
class LaunchStreamlitView(View):
    def get(self, request):
        bot_folder = r"C:\Users\12ELEVEN\Desktop\etan-website\bot"
        venv_activate = rf"{bot_folder}\botvenv\Scripts\activate.bat"
        streamlit_path = rf"{bot_folder}\app.py"

        command = f'cmd /k "{venv_activate} && streamlit run {streamlit_path}"'
        subprocess.Popen(command, cwd=bot_folder, shell=True)

        return JsonResponse({"status": "ok"})
