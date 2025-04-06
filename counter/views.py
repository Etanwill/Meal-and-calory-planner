from django.shortcuts import render
import google.generativeai as genai
import os
# ygbOdmqiBwBzF66IBtS/uA==4r4AR2DSPk8gEfi2 calory api key
# AIzaSyBYk7qyLWYuqoSiMTYp_YFMlt1C0LqOYpo recommendation api key
# Create your views here.

os.environ["GOOGLE_API_KEY"] = "AIzaSyCeSq_yeCu7uPIoZRtYoCmLPvNPowHdjU8"
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

#initialize model
model = genai.GenerativeModel("gemini-1.5-pro")

#custom function
def generate_recommendation(dietary_preferences, fitness_goal, lifestyle_factor, dietary_restrictions, health_condition, your_query):
    
    model = genai.GenerativeModel(
        model_name="gemini-1.5-pro",
        generation_config={
            "temperature": 1,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 8192,
            "response_mime_type": "text/plain",
        }
    )

    chat_session = model.start_chat(
        history=[]
    )

    
    prompt = f"""
Can you suggest a comprehensive plan that includes a diet and workout options for better fitness for this user:
- Dietary preferences: {dietary_preferences}
- Fitness goal: {fitness_goal}
- Lifestyle factor: {lifestyle_factor}
- Dietary restrictions: {dietary_restrictions}
- Health condition: {health_condition}
- Your query: {your_query}

Please provide the following:
1. Diet Recommendations (list 5 diet types)
2. Workout Options (list 5 workout options)
3. Meal Suggestions:
   - 5 breakfast ideas
   - 5 dinner ideas
4. Additional Recommendations (include useful snacks, supplements, or hydration tips)
formated it well so it should be easily understandable and in point form
"""


    response = model.generate_content(prompt)
    return response.text.strip()





def home(request):
    import json
    import requests
    if request.method == 'POST':
        query = request.POST['query'] #get query from home page
        api_url = 'https://api.api-ninjas.com/v1/nutrition?query='
        api_request = requests.get(api_url + query, headers={'X-Api-Key': 'ygbOdmqiBwBzF66IBtS/uA==4r4AR2DSPk8gEfi2'})
        if api_request.status_code == 200: # if request is successful
            api_data = api_request.json()
            if api_data:  # Check if the API returned data
                # Get the first item from the API response
                food_data = api_data[0]
                
                # Calculate the total
                total = (
                    food_data.get("carbohydrates_total_g", 0) +
                    food_data.get("cholesterol_mg", 0) + # if key do not exixt return 0
                    food_data.get("fat_saturated_g", 0) +
                    food_data.get("fat_total_g", 0) +
                    food_data.get("fiber_g", 0) +
                    food_data.get("potassium_mg", 0) +
                    food_data.get("sugar_g", 0)
                )

        try:
            api =json.loads(api_request.content)
            print(api_request.content)
        except Exception as e:
            api = "oops! there was an error"
            print(e)
        return render(request, 'home.html', {'api':api, 'total':total}) #display on homepage

    else:
        return render(request, 'home.html', {'query:':'Enter valid query'})

def recomendation(request):
    if request.method == 'POST':
        # Collect form data
        dietary_preferences = request.POST['dietary_preferences']
        fitness_goal = request.POST['fitness_goal']
        lifestyle_factor = request.POST['lifestyle_factor']
        dietary_restrictions = request.POST['dietary_restrictions']
        health_condition = request.POST['health_condition']
        your_query = request.POST['your_query']

        # Generate the recommendation text
        recomendation_text = generate_recommendation(
            dietary_preferences, fitness_goal, lifestyle_factor, dietary_restrictions, health_condition, your_query
        )

        recommendations = {
            "diet_types" : [],
            "workouts": [],
            "breakfasts": [],
            "dinners":[],
            "additional_tips": []
        }

        
        #split and map response on keyword
        current_section = None
        for line in recomendation_text.splitlines():
            if "Diet Recommendations" in line:
                current_section = 'diet_types'
            elif  "Workout Options" in line:
                current_section = 'workouts'
            elif  "Meal Suggestions" in line:
                current_section = 'breakfasts'
            elif  "Dinner" in line:
                current_section = 'dinners'
            elif  "Additional Recommendations" in line:
                current_section = 'additional_tips'
            elif line.strip() and current_section:
                recommendations[current_section].append(line.strip())
            

        print(recommendations)
        # Return the recommendation text to the template
        return render(request, 'recomendation.html', {'recommendations': recommendations})

    # If the request is GET (no form submission), just render the empty form
    return render(request, 'recomendation.html', {'recommendations': None})
