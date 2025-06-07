from django.shortcuts import render, redirect
from .models import UserRecommendation, FoodQueryForm
import requests
from .recommendation_profiles import PERSONALIZED_RECOMMENDATIONS
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from .forms import LoginForm, RegisterForm
from tika import parser
import json
import markdown
from google import genai


PDF_PATH = r"C:\\Users\\Arthur\\Desktop\\Meal-and-calory-planner2\\real_food.pdf"

def read_file(path):
    text = parser.from_file(path)
    return text["content"]

DATA = read_file(PDF_PATH)
print("data is", DATA[:200])








def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)  # Connexion de l'utilisateur
            print("Connexion réussie pour :", user.username)  # Debug
            return redirect('home')
        else:
            print("Erreur login :", form.errors)  # Debug erreurs
            return render(request, 'login.html', {'form': form})
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})


def signup_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
        else:
            return render(request, 'signup.html', {'form': form})
    else:
        form = RegisterForm()
    return render(request, 'signup.html', {'form': form})


def logout_view(request):
    auth_logout(request)
    return redirect('login')


@login_required(login_url='login')
def home(request):
    print("User authentifié ? :", request.user.is_authenticated)
    print("User connecté :", request.user.username)
    return render(request, 'home.html')



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

        if score > best_score:
            best_score = score
            best_match = profile

        if matched and score > fallback_score:
            fallback_score = score
            fallback_match = profile

    final_match = best_match if best_score > 0 else fallback_match

    if final_match:
        return {
            "diet_types": final_match["diet_types"],
            "workouts": final_match["workouts"],
            "breakfasts": final_match["breakfasts"],
            "dinners": final_match["dinners"],
            "additional_tips": final_match["additional_tips"]
        }

    return {
        "diet_types": ["Balanced diet", "Whole food based", "Low sugar", "Low sodium", "Anti-inflammatory"],
        "workouts": ["Walking", "Yoga", "Light strength", "Pilates", "Stretching"],
        "breakfasts": ["Oatmeal with fruits", "Greek yogurt", "Eggs and toast", "Smoothie bowl", "Protein pancakes"],
        "dinners": ["Grilled chicken and veggies", "Salmon with quinoa", "Lentil soup", "Zucchini noodles", "Tofu stir fry"],
        "additional_tips": ["Drink 2L water/day", "Avoid processed foods", "Include healthy snacks", "Use natural supplements", "Sleep 7-8 hours"]
    }


@login_required(login_url='login')
def home(request):
    if request.method == 'POST':
        query = request.POST.get('query')
        api = "No data found."

        # === API NINJAS: Get full nutrition info ===
        api_url = 'https://api.api-ninjas.com/v1/nutrition?query='
        headers1 = {'X-Api-Key': 'ygbOdmqiBwBzF66IBtS/uA==4r4AR2DSPk8gEfi2'}

        try:
            api_request = requests.get(api_url + query, headers=headers1)
            if api_request.status_code == 200:
                api_data = api_request.json()
                if api_data:
                    api = api_data
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
        context = {}
        try:
            response = requests.post(c_url, json=data, headers=headers2)
            if response.status_code == 200:
                nutritionix_data = response.json()
                if "foods" in nutritionix_data and nutritionix_data["foods"]:
                    food = nutritionix_data["foods"][0]
                    context = {
                        'carbs': food.get("nf_total_carbohydrate", 0),
                        'total': food.get("nf_calories", 0),
                        'chols': food.get("nf_cholesterol", 0),
                        'fat_sat': food.get("nf_saturated_fat", 0),
                        'fat_total': food.get("nf_total_fat", 0),
                        'fibre': food.get("nf_dietary_fiber", 0),
                        'potasium': food.get("nf_potassium", 0),
                        'sodium': food.get("nf_sodium", 0),
                        'sugar': food.get("nf_sugars", 0),
                        'proteins': food.get("nf_protein", 0),
                        'api': api
                    }
                else:
                    context['error'] = "⚠️ No food data found. Please try another item."
            else:
                context['error'] = f"⚠️ Nutritionix API error: {response.status_code}"
        except Exception as e:
            context['error'] = f"⚠️ Something went wrong: {str(e)}"

        return render(request, 'home.html', context)
    else:
        return render(request, 'home.html', {'query': 'Enter a valid query'})


def recomendation(request):
    if request.method == 'POST':
        data = {
            'dietary_preferences': request.POST.get('dietary_preferences', ''),
            'fitness_goal': request.POST.get('fitness_goal', ''),
            'lifestyle_factor': request.POST.get('lifestyle_factor', ''),
            'dietary_restrictions': request.POST.get('dietary_restrictions', ''),
            'health_condition': request.POST.get('health_condition', ''),
            'your_query': request.POST.get('your_query', ''),
        }

        UserRecommendation.objects.create(**data)
        recommendations = generate_manual_recommendation(data)
        return render(request, 'recomendation.html', {'recommendations': recommendations})

    return render(request, 'recomendation.html', {'recommendations': None})

def get_answer(prompt):
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )
        return response.text
    except Exception as e:
        return "Erreur lors de la génération de la réponse : " + str(e)



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

            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=user_message
            )
            return JsonResponse({'reply': response.text})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request'}, status=405)
