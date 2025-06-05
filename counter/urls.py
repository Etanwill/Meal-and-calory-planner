from django.urls import path, include
from . import views
from .views import LaunchStreamlitView, UserViewSet, logout_view
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'users', UserViewSet)

urlpatterns = [
    path('', views.login_view, name='login'),  # Page de connexion par défaut
    path('register/', views.register_view, name='register'),
    path('home/', views.home, name='home'),  # Redirection après connexion
    path('recommendation/', views.recommendation, name='recommendation'),

    
    path('launch-streamlit/', LaunchStreamlitView.as_view(), name='launch_streamlit'),
    path('api/', include(router.urls)),  # API REST pour les utilisateurs
    path('logout/', logout_view, name='logout'),
]
