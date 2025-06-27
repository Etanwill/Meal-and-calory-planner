from rest_framework import serializers
from counter.models import CustomUser  # ou get_user_model()

class UserSerializer(serializers.ModelSerializer):#create a serializer
    class Meta:
        model = CustomUser   #indicate which model to serialize
        fields = ['id', 'username', 'email',]  # fields to get via the api
