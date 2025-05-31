# === Imports ===
import time
import os
from google import genai


GEMINI_API_KEY = "AIzaSyDnBFJklLBH4OYPnvphJ1DAu8V7e38CvQs"
client = genai.Client(api_key=GEMINI_API_KEY)





def get_answer(prompt):
    response = client.models.generate_content(
    model="gemini-2.0-flash",
    contents=prompt)
    return response.text