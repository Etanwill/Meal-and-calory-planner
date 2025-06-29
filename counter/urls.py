from django.urls import path
from . import views
from django.urls import path, include




urlpatterns = [
    path('', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('home/', views.home, name='home'),
    path('logout/', views.logout_view, name='logout'),
    
    # autres chemins existants :
    path('recomendation/', views.recomendation, name='recomendation'),
    path('cameroon-recipe/', views.food_chat_view, name='cameroon_recipe'),
    path('chatbot/chat/', views.chat_with_ai, name='chat_with_ai'),
    path('api/', include('api.urls')),
    path('about/', views.about, name='about'),


    
   
]
