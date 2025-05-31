from django.shortcuts import render, redirect
from .models import UserRecommendation, FoodQueryForm
import requests
from .recommendation_profiles import PERSONALIZED_RECOMMENDATIONS
import subprocess
from django.http import HttpResponse
from django.views import View
from .langchain_backend import get_answer
import json
import markdown
from google import genai
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse


from tika import parser

PDF_PATH = r"C:\Users\12ELEVEN\Desktop\etan-website\Food-Generative-ai\Data\real_food.pdf"
def read_file(path):
    text = parser.from_file(path)
    return text["content"]

DATA = read_file(PDF_PATH)
print("data is", DATA[:200])

# Fonction de génération de recommandations personnalisées


def generate_manual_recommendation(data):
    best_score = 0
    best_match = None
    fallback_match = None
    fallback_score = 0

    for profile in PERSONALIZED_RECOMMENDATIONS:
        score = 0
        conditions = profile["conditions"]
        matched = False

        for key, value in conditions.items():
            if key in data:
                user_value = data[key].lower()
                profile_value = value.lower()

                if user_value == profile_value:
                    score += 2
                    matched = True
                elif profile_value in user_value or user_value in profile_value:
                    score += 1
                    matched = True

        # Always track the best match by score
        if score > best_score:
            best_score = score
            best_match = profile

        # Track fallback: any match at all, but lower priority than best_match
        if matched and score > fallback_score:
            fallback_score = score
            fallback_match = profile

    # Priority: best_match > fallback_match > nothing
    final_match = best_match if best_score > 0 else fallback_match

    if final_match:
        return {
            "diet_types": final_match["diet_types"],
            "workouts": final_match["workouts"],
            "breakfasts": final_match["breakfasts"],
            "dinners": final_match["dinners"],
            "additional_tips": final_match["additional_tips"]
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
# ygbOdmqiBwBzF66IBtS/uA==4r4AR2DSPk8gEfi2



def home(request):
    import json
    import requests

    if request.method == 'POST':
        query = request.POST.get('query')
        total = 0
        api = "No data found."

        # === API NINJAS: Get full nutrition info ===
        api_url = 'https://api.api-ninjas.com/v1/nutrition?query='
        headers1 = {'X-Api-Key': 'ygbOdmqiBwBzF66IBtS/uA==4r4AR2DSPk8gEfi2'}

        try:
            api_request = requests.get(api_url + query, headers=headers1)
            if api_request.status_code == 200:
                api_data = api_request.json()
                if api_data:
                    api = api_data  # You pass this to the template
            else:
                api = f"API-Ninjas Error: {api_request.status_code}"
        except Exception as e:
            api = f"API-Ninjas Error: {str(e)}"

        # === NUTRITIONIX: Only get calories ===
        c_url = "https://trackapi.nutritionix.com/v2/natural/nutrients"
        headers2 = {
            "x-app-id": "f20c2372",
            "x-app-key": "853271f146cb44f2e118a6a9d2b4f00e",
            "Content-Type": "application/json"
        }
        data = {
            "query": query,
            "timezone": "US/Eastern"
        }

        try:
            response = requests.post(c_url, json=data, headers=headers2)
            if response.status_code == 200:
                nutritionix_data = response.json()
                if "foods" in nutritionix_data and nutritionix_data["foods"]:
                    total = nutritionix_data["foods"][0].get("nf_calories", 0)
            else:
                print(f"Nutritionix Error: {response.status_code}")
        except Exception as e:
            print(f"Nutritionix Error: {str(e)}")

        return render(request, 'home.html', {'api': api, 'total': total})

    else:
        return render(request, 'home.html', {'query': 'Enter a valid query'})

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





def food_chat_view(request):
    answer_ingredients = ""
    answer_directions = ""
    
    if request.method == "POST":
        form = FoodQueryForm(request.POST)
        if form.is_valid():
            food_name = form.cleaned_data["food_name"]
            ingredients_prompt = f"According to the data {DATA}, list everything under 'Ingredients for {food_name}:'"
            directions_prompt = f"Provide the detailed description concerning the preparation of {food_name} according to the following data: {DATA}, don't care about the ingredients and start the response withHere is a detailed description of the preparation of {food_name}, based on the provided recipe, focusing on the steps and techniques:"

            answer_ingredients = markdown.markdown(get_answer(ingredients_prompt))
            answer_directions = markdown.markdown(get_answer(directions_prompt))
    else:
        form = FoodQueryForm()

    return render(request, "chatbot/chat.html", {
        "form": form,
        "answer_ingredients": answer_ingredients,
        "answer_directions": answer_directions,
    })


GEMINI_API_KEY = "AIzaSyDnBFJklLBH4OYPnvphJ1DAu8V7e38CvQs"
client = genai.Client(api_key=GEMINI_API_KEY)

@csrf_exempt
def chat_with_ai(request):
    if request.method == 'POST':
        try:
            body = json.loads(request.body)
            user_message = body.get('message', '')

            if not user_message:
                return JsonResponse({'error': 'Empty message'}, status=400)

            response = client.models.generate_content(model="gemini-2.0-flash",
    contents=user_message)
            return JsonResponse({'reply': response.text})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request'}, status=405)