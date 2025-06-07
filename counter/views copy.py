from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.decorators import login_required
from .models import UserRecommendation
import requests
from .recommendation_profiles import PERSONALIZED_RECOMMENDATIONS

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'signup.html', {'form': form})

@login_required(login_url='login')
def home(request):
    api = None
    total = 0
    if request.method == "POST":
        query = request.POST['query']
        url = "https://trackapi.nutritionix.com/v2/natural/nutrients"
        headers = {
            "x-app-id": "f20c2372",
            "x-app-key": "853271f146cb44f2e118a6a9d2b4f00e",
            "Content-Type": "application/json"
        }
        data = {"query": query, "timezone": "US/Eastern"}
        try:
            response = requests.post(url, json=data, headers=headers)
            if response.status_code == 200:
                data = response.json()
                if "foods" in data:
                    api = [data["foods"][0]]
                    total = api[0]["nf_calories"]
                else:
                    api = "Erreur dans les données reçues."
            else:
                api = f"Erreur {response.status_code}"
        except Exception as e:
            api = f"Erreur : {str(e)}"
    return render(request, "home.html", {"api": api, "total": total})

def logout_view(request):
    logout(request)
    return redirect('login')

def recomendation(request):
    if request.method == 'POST':
        data = {
            'dietary_preferences': request.POST['dietary_preferences'],
            'fitness_goal': request.POST['fitness_goal'],
            'lifestyle_factor': request.POST['lifestyle_factor'],
            'dietary_restrictions': request.POST['dietary_restrictions'],
            'health_condition': request.POST['health_condition'],
            'your_query': request.POST['your_query'],
        }
        UserRecommendation.objects.create(**data)
        recommendations = generate_manual_recommendation(data)
        return render(request, 'recomendation.html', {'recommendations': recommendations})
    return render(request, 'recomendation.html', {'recommendations': None})

def generate_manual_recommendation(data):
    for profile in PERSONALIZED_RECOMMENDATIONS:
        if all(value.lower() in data.get(key, '').lower() for key, value in profile["conditions"].items()):
            return profile
    return {
        "diet_types": ["Balanced diet", "Whole food based", "Low sugar"],
        "workouts": ["Walking", "Yoga", "Stretching"],
        "breakfasts": ["Oatmeal", "Greek yogurt"],
        "dinners": ["Grilled chicken", "Lentil soup"],
        "additional_tips": ["Drink water", "Sleep 8h", "Avoid sugar"]
    }
