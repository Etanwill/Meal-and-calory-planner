from django.shortcuts import render
from .models import UserRecommendation
import requests
from .recommendation_profiles import PERSONALIZED_RECOMMENDATIONS

# Fonction de génération de recommandations personnalisées


def generate_manual_recommendation(data):
    for profile in PERSONALIZED_RECOMMENDATIONS:
        match = True
        for key, value in profile["conditions"].items():
            if key in data and value.lower() not in data[key].lower():
                match = False
                break
        if match:
            return {
                "diet_types": profile["diet_types"],
                "workouts": profile["workouts"],
                "breakfasts": profile["breakfasts"],
                "dinners": profile["dinners"],
                "additional_tips": profile["additional_tips"]
            }

    # Si aucun profil ne correspond, suggestions par défaut
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
