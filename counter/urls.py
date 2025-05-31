from django.urls import path
from . import views
from .views import food_chat_view, chat_with_ai

urlpatterns = [
    path('', views.home, name= 'home'),
    path('recomendation/', views.recomendation, name='recomendation'),
    path('cameroon-recipe/', food_chat_view, name='cameroon_recipe'),
    path('chatbot/chat/', chat_with_ai, name='chat_with_ai'),
]