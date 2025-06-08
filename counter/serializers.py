from rest_framework import serializers
from counter.models import CustomUser  # ou get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email']  # ajoute d'autres champs si besoin
