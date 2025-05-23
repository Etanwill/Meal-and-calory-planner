from django.shortcuts import render, redirect
from .models import UserRecommendation
import requests
from .recommendation_profiles import PERSONALIZED_RECOMMENDATIONS
import subprocess
from django.http import HttpResponse
from django.views import View


# Fonction de génération de recommandations personnalisées


def generate_manual_recommendation(data):
    best_score = 0
    best_match = None

    for profile in PERSONALIZED_RECOMMENDATIONS:
        score = 0
        conditions = profile["conditions"]

        for key, value in conditions.items():
            if key in data:
                if value.lower() == data[key].lower():
                    score += 2  # exact match
                elif value.lower() in data[key].lower() or data[key].lower() in value.lower():
                    score += 1  # partial match

        if score > best_score:
            best_score = score
            best_match = profile

    if best_match:
        return {
            "diet_types": best_match["diet_types"],
            "workouts": best_match["workouts"],
            "breakfasts": best_match["breakfasts"],
            "dinners": best_match["dinners"],
            "additional_tips": best_match["additional_tips"]
        }

    # Default suggestion if no match found
    return {
        "diet_types": ["Balanced diet", "Whole food based", "Low sugar", "Low sodium", "Anti-inflammatory"],
        "workouts": ["Walking", "Yoga", "Light strength", "Pilates", "Stretching"],
        "breakfasts": ["Oatmeal with fruits", "Greek yogurt", "Eggs and toast", "Smoothie bowl", "Protein pancakes"],
        "dinners": ["Grilled chicken and veggies", "Salmon with quinoa", "Lentil soup", "Zucchini noodles", "Tofu stir fry"],
        "additional_tips": ["Drink 2L water/day", "Avoid processed foods", "Include healthy snacks", "Use natural supplements", "Sleep 7-8 hours"]
    }


# Vue de la page d'accueil (optionnelle, simple affichage)




def home(request):
    api = None
    total = 0
    if request.method == "POST":
        query = request.POST['query']
        url = "https://trackapi.nutritionix.com/v2/natural/nutrients"
        headers = {
            "x-app-id": "f20c2372",
            "x-app-key": "853271f146cb44f2e118a6a9d2b4f00e",  # Retirer le caractère '—' qui était ici
            "Content-Type": "application/json"
        }
        data = {
            "query": query,
            "timezone": "US/Eastern"
        }

        try:
            # Envoi de la requête POST
            response = requests.post(url, json=data, headers=headers)

            # Vérification de la réponse
            if response.status_code == 200:
                data = response.json()
                if "foods" in data:
                    api = [data["foods"][0]]
                    total = api[0]["nf_calories"]
                else:
                    api = "Oops! There was an error with the response data."
            else:
                api = f"Oops! There was an error. Status code: {response.status_code}"
        except Exception as e:
            api = f"An error occurred: {str(e)}"

    return render(request, "home.html", {"api": api, "total": total})




# Vue de la page de recommandation
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

        # Enregistrer les infos utilisateur dans la base de données
        UserRecommendation.objects.create(**data)

        # Générer les recommandations personnalisées
        recommendations = generate_manual_recommendation(data)

        return render(request, 'recomendation.html', {'recommendations': recommendations})

    return render(request, 'recomendation.html', {'recommendations': None})


class LaunchStreamlitView(View):
    def get(self, request):
        bot_folder = r"C:\Users\12ELEVEN\Desktop\etan-website\bot"
        venv_activate = rf"{bot_folder}\botvenv\Scripts\activate.bat"
        streamlit_path = rf"{bot_folder}\app.py"

        # Use bash to activate venv and launch Streamlit
        command = f'cmd /k "{venv_activate} && streamlit run {streamlit_path}"'

        # Run in a separate terminal or background process
        subprocess.Popen(command, cwd=bot_folder, shell=True)

        return JsonResponse({"status": "ok"})
