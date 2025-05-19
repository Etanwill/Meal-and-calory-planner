from django.urls import path
from . import views
from .views import LaunchStreamlitView
urlpatterns = [
    path('', views.home, name= 'home'),
    path('recomendation/', views.recomendation, name='recomendation'),
    path('launch-streamlit/', LaunchStreamlitView.as_view(), name='launch_streamlit')
]